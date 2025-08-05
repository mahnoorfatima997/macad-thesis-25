"""
Update all benchmarking diagrams with accurate system architecture
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Rectangle, FancyArrowPatch
import numpy as np

# THESIS COLORS - ONLY THESE COLORS ARE ALLOWED
THESIS_COLORS = {
    # Main colors
    'primary_dark': '#4f3a3e',      # Dark burgundy
    'primary_purple': '#5c4f73',    # Deep purple
    'primary_violet': '#784c80',    # Rich violet
    'primary_rose': '#b87189',      # Dusty rose
    'primary_pink': '#cda29a',      # Soft pink
    
    # Neutral tones
    'neutral_light': '#e0ceb5',     # Light beige
    'neutral_warm': '#dcc188',      # Warm sand
    'neutral_orange': '#d99c66',    # Soft orange
    
    # Accent colors
    'accent_coral': '#cd766d',      # Coral red
    'accent_magenta': '#cf436f',    # Bright magenta
}

# For easier reference in code
COLORS = THESIS_COLORS

def create_comprehensive_data_flow():
    """Create comprehensive data flow diagram"""
    fig, ax = plt.subplots(figsize=(16, 12))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 12)
    ax.axis('off')
    
    # Title
    ax.text(8, 11.5, 'MEGA Architectural Mentor - Complete Data Flow', 
            fontsize=20, weight='bold', ha='center', color=COLORS['dark'])
    
    # Stage 1: Test Dashboard
    stage1_box = FancyBboxPatch((0.5, 8.5), 3.5, 2.5, 
                                boxstyle="round,pad=0.1", 
                                facecolor=COLORS['primary'], 
                                edgecolor=COLORS['dark'], 
                                linewidth=2, alpha=0.9)
    ax.add_patch(stage1_box)
    ax.text(2.25, 10.3, 'TEST DASHBOARD', fontsize=14, weight='bold', 
            ha='center', va='center', color='white')
    ax.text(2.25, 9.8, 'launch_test_dashboard.py', fontsize=10, 
            ha='center', va='center', color='white')
    ax.text(2.25, 9.3, '• User Sessions', fontsize=9, 
            ha='center', va='center', color='white')
    ax.text(2.25, 8.9, '• Real-time Assessment', fontsize=9, 
            ha='center', va='center', color='white')
    
    # Stage 2: Data Collection
    data_box = FancyBboxPatch((5, 8.5), 3.5, 2.5,
                              boxstyle="round,pad=0.1",
                              facecolor=COLORS['secondary'],
                              edgecolor=COLORS['dark'],
                              linewidth=2, alpha=0.9)
    ax.add_patch(data_box)
    ax.text(6.75, 10.3, 'DATA COLLECTION', fontsize=14, weight='bold',
            ha='center', va='center', color='white')
    ax.text(6.75, 9.8, 'thesis_data/', fontsize=10,
            ha='center', va='center', color='white')
    ax.text(6.75, 9.3, '• interactions_*.csv', fontsize=9,
            ha='center', va='center', color='white')
    ax.text(6.75, 8.9, '• metrics_*.csv', fontsize=9,
            ha='center', va='center', color='white')
    
    # Stage 3: Benchmarking Analysis
    analysis_box = FancyBboxPatch((9.5, 8.5), 3.5, 2.5,
                                  boxstyle="round,pad=0.1",
                                  facecolor=COLORS['accent'],
                                  edgecolor=COLORS['dark'],
                                  linewidth=2, alpha=0.9)
    ax.add_patch(analysis_box)
    ax.text(11.25, 10.3, 'BENCHMARKING', fontsize=14, weight='bold',
            ha='center', va='center', color='white')
    ax.text(11.25, 9.8, 'run_benchmarking.py', fontsize=10,
            ha='center', va='center', color='white')
    ax.text(11.25, 9.3, '• Analysis Pipeline', fontsize=9,
            ha='center', va='center', color='white')
    ax.text(11.25, 8.9, '• Report Generation', fontsize=9,
            ha='center', va='center', color='white')
    
    # Stage 4: Results Dashboard
    dashboard_box = FancyBboxPatch((13.5, 8.5), 2, 2.5,
                                   boxstyle="round,pad=0.1",
                                   facecolor=COLORS['dark'],
                                   edgecolor=COLORS['dark'],
                                   linewidth=2, alpha=0.9)
    ax.add_patch(dashboard_box)
    ax.text(14.5, 10.3, 'DASHBOARD', fontsize=14, weight='bold',
            ha='center', va='center', color='white')
    ax.text(14.5, 9.8, 'benchmark_', fontsize=10,
            ha='center', va='center', color='white')
    ax.text(14.5, 9.4, 'dashboard.py', fontsize=10,
            ha='center', va='center', color='white')
    ax.text(14.5, 8.9, '• Visualize', fontsize=9,
            ha='center', va='center', color='white')
    
    # Processing Components
    components = [
        ('Linkography\nAnalysis', 2, 6, COLORS['primary']),
        ('Graph ML\nProcessing', 5, 6, COLORS['secondary']),
        ('Proficiency\nClassifier', 8, 6, COLORS['accent']),
        ('Statistical\nAnalysis', 11, 6, COLORS['dark']),
        ('Report\nGenerator', 14, 6, COLORS['primary'])
    ]
    
    for name, x, y, color in components:
        comp_box = FancyBboxPatch((x-1, y-0.5), 2, 1.5,
                                  boxstyle="round,pad=0.1",
                                  facecolor=color,
                                  edgecolor=COLORS['dark'],
                                  linewidth=1.5, alpha=0.8)
        ax.add_patch(comp_box)
        ax.text(x, y+0.25, name, fontsize=10, weight='bold',
                ha='center', va='center', color='white',
                multialignment='center')
    
    # Data Storage
    storage_boxes = [
        ('Session Metrics\nCSV Files', 3, 3.5, COLORS['light']),
        ('Linkography\nJSON/HTML', 6, 3.5, COLORS['light']),
        ('Evaluation\nReports', 9, 3.5, COLORS['light']),
        ('Master Metrics\nAggregated', 12, 3.5, COLORS['light'])
    ]
    
    for name, x, y, color in storage_boxes:
        storage_box = FancyBboxPatch((x-1.25, y-0.5), 2.5, 1.2,
                                     boxstyle="round,pad=0.1",
                                     facecolor=color,
                                     edgecolor=COLORS['border'],
                                     linewidth=1.5)
        ax.add_patch(storage_box)
        ax.text(x, y, name, fontsize=9,
                ha='center', va='center', color=COLORS['text'],
                multialignment='center')
    
    # Arrows - positioned UNDER boxes
    # Horizontal flow arrows (main pipeline)
    arrow_props = dict(arrowstyle='->', lw=2.5, color=COLORS['dark'])
    
    # Test Dashboard to Data Collection
    ax.annotate('', xy=(5, 9.75), xytext=(4, 9.75),
                arrowprops=arrow_props)
    
    # Data Collection to Benchmarking
    ax.annotate('', xy=(9.5, 9.75), xytext=(8.5, 9.75),
                arrowprops=arrow_props)
    
    # Benchmarking to Dashboard
    ax.annotate('', xy=(13.5, 9.75), xytext=(13, 9.75),
                arrowprops=arrow_props)
    
    # Vertical arrows to components
    component_arrow_props = dict(arrowstyle='->', lw=1.5, color=COLORS['border'])
    
    # From Data Collection to components
    ax.annotate('', xy=(2, 7.5), xytext=(2.25, 8.5),
                arrowprops=component_arrow_props)
    ax.annotate('', xy=(5, 7.5), xytext=(6.75, 8.5),
                arrowprops=component_arrow_props)
    ax.annotate('', xy=(8, 7.5), xytext=(8, 8.5),
                arrowprops=component_arrow_props)
    
    # From components to storage
    ax.annotate('', xy=(3, 4.7), xytext=(2, 5),
                arrowprops=component_arrow_props)
    ax.annotate('', xy=(6, 4.7), xytext=(5, 5),
                arrowprops=component_arrow_props)
    ax.annotate('', xy=(9, 4.7), xytext=(8, 5),
                arrowprops=component_arrow_props)
    ax.annotate('', xy=(12, 4.7), xytext=(11, 5),
                arrowprops=component_arrow_props)
    
    # Export options
    export_box = FancyBboxPatch((13, 1.5), 2.5, 1.5,
                                boxstyle="round,pad=0.1",
                                facecolor=COLORS['secondary'],
                                edgecolor=COLORS['dark'],
                                linewidth=2, alpha=0.9)
    ax.add_patch(export_box)
    ax.text(14.25, 2.7, 'EXPORT', fontsize=12, weight='bold',
            ha='center', va='center', color='white')
    ax.text(14.25, 2.2, 'HTML Reports', fontsize=9,
            ha='center', va='center', color='white')
    ax.text(14.25, 1.8, 'JSON/CSV', fontsize=9,
            ha='center', va='center', color='white')
    
    # Export arrow
    ax.annotate('', xy=(14.25, 3), xytext=(14.5, 8.5),
                arrowprops=dict(arrowstyle='->', lw=2, color=COLORS['secondary']))
    
    # Key insights box
    insights_box = FancyBboxPatch((0.5, 0.5), 11, 1.5,
                                  boxstyle="round,pad=0.1",
                                  facecolor=COLORS['light'],
                                  edgecolor=COLORS['border'],
                                  linewidth=1.5)
    ax.add_patch(insights_box)
    ax.text(6, 1.6, 'KEY FEATURES', fontsize=11, weight='bold',
            ha='center', va='center', color=COLORS['dark'])
    ax.text(2.5, 1, '• Real cognitive assessment', fontsize=9,
            ha='left', va='center', color=COLORS['text'])
    ax.text(2.5, 0.6, '• No hardcoded values', fontsize=9,
            ha='left', va='center', color=COLORS['text'])
    ax.text(6.5, 1, '• Comprehensive analysis pipeline', fontsize=9,
            ha='left', va='center', color=COLORS['text'])
    ax.text(6.5, 0.6, '• Professional HTML reports', fontsize=9,
            ha='left', va='center', color=COLORS['text'])
    
    plt.tight_layout()
    plt.savefig('comprehensive_data_flow.png', dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.close()
    
    print("Created: comprehensive_data_flow.png")

def create_metric_calculation_flow():
    """Create detailed metric calculation flow diagram"""
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Title
    ax.text(7, 9.5, 'Cognitive Metric Calculation Flow', 
            fontsize=18, weight='bold', ha='center', color=COLORS['dark'])
    
    # Input: User Response
    input_box = FancyBboxPatch((1, 7.5), 3, 1.5,
                               boxstyle="round,pad=0.1",
                               facecolor=COLORS['primary'],
                               edgecolor=COLORS['dark'],
                               linewidth=2)
    ax.add_patch(input_box)
    ax.text(2.5, 8.25, 'USER RESPONSE', fontsize=12, weight='bold',
            ha='center', va='center', color='white')
    
    # Analysis Components
    components = [
        ('Keyword\nDetection', 1, 5.5),
        ('Question\nDepth', 3.5, 5.5),
        ('Response\nLength', 6, 5.5),
        ('Thinking\nIndicators', 8.5, 5.5),
        ('AI Reliance\nPatterns', 11, 5.5)
    ]
    
    for name, x, y in components:
        comp_box = FancyBboxPatch((x-0.75, y-0.5), 1.5, 1.2,
                                  boxstyle="round,pad=0.05",
                                  facecolor=COLORS['secondary'],
                                  edgecolor=COLORS['dark'],
                                  linewidth=1.5, alpha=0.9)
        ax.add_patch(comp_box)
        ax.text(x, y, name, fontsize=9, weight='bold',
                ha='center', va='center', color='white',
                multialignment='center')
    
    # Core Metrics Calculation
    metrics = [
        ('Prevention Rate\nCalculation', 3, 3.5, COLORS['accent']),
        ('Deep Thinking\nAssessment', 7, 3.5, COLORS['accent']),
        ('Improvement\nScore', 11, 3.5, COLORS['accent'])
    ]
    
    for name, x, y, color in metrics:
        metric_box = FancyBboxPatch((x-1, y-0.5), 2, 1.2,
                                    boxstyle="round,pad=0.1",
                                    facecolor=color,
                                    edgecolor=COLORS['dark'],
                                    linewidth=2)
        ax.add_patch(metric_box)
        ax.text(x, y, name, fontsize=10, weight='bold',
                ha='center', va='center', color='white',
                multialignment='center')
    
    # Final Output
    output_box = FancyBboxPatch((5, 1), 4, 1.5,
                                boxstyle="round,pad=0.1",
                                facecolor=COLORS['dark'],
                                edgecolor=COLORS['dark'],
                                linewidth=2)
    ax.add_patch(output_box)
    ax.text(7, 1.75, 'COGNITIVE METRICS', fontsize=12, weight='bold',
            ha='center', va='center', color='white')
    
    # Arrows
    arrow_props = dict(arrowstyle='->', lw=1.5, color=COLORS['border'])
    
    # From input to components
    for x in [1, 3.5, 6, 8.5, 11]:
        ax.annotate('', xy=(x, 6.2), xytext=(2.5, 7.5),
                    arrowprops=arrow_props)
    
    # From components to metrics
    ax.annotate('', xy=(3, 4.2), xytext=(1, 5),
                arrowprops=arrow_props)
    ax.annotate('', xy=(3, 4.2), xytext=(3.5, 5),
                arrowprops=arrow_props)
    
    ax.annotate('', xy=(7, 4.2), xytext=(6, 5),
                arrowprops=arrow_props)
    ax.annotate('', xy=(7, 4.2), xytext=(8.5, 5),
                arrowprops=arrow_props)
    
    ax.annotate('', xy=(11, 4.2), xytext=(11, 5),
                arrowprops=arrow_props)
    
    # From metrics to output
    ax.annotate('', xy=(7, 2.5), xytext=(3, 3),
                arrowprops=arrow_props)
    ax.annotate('', xy=(7, 2.5), xytext=(7, 3),
                arrowprops=arrow_props)
    ax.annotate('', xy=(7, 2.5), xytext=(11, 3),
                arrowprops=arrow_props)
    
    # Key formulas
    formula_box = FancyBboxPatch((0.5, 0.2), 13, 0.6,
                                 boxstyle="round,pad=0.05",
                                 facecolor=COLORS['light'],
                                 edgecolor=COLORS['border'],
                                 linewidth=1)
    ax.add_patch(formula_box)
    ax.text(7, 0.5, 'Prevention Rate = 1 - (Direct Answer Keywords / Total Keywords) × Response Quality Factor',
            fontsize=9, ha='center', va='center', color=COLORS['text'])
    
    plt.tight_layout()
    plt.savefig('metric_calculation_flow_updated.png', dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    
    print("Created: metric_calculation_flow_updated.png")

def create_linkography_analysis_flow():
    """Create linkography analysis flow diagram"""
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Title
    ax.text(7, 9.5, 'Linkography Analysis Pipeline', 
            fontsize=18, weight='bold', ha='center', color=COLORS['dark'])
    
    # Session Data Input
    input_box = FancyBboxPatch((0.5, 7.5), 3, 1.5,
                               boxstyle="round,pad=0.1",
                               facecolor=COLORS['primary'],
                               edgecolor=COLORS['dark'],
                               linewidth=2)
    ax.add_patch(input_box)
    ax.text(2, 8.25, 'SESSION DATA', fontsize=12, weight='bold',
            ha='center', va='center', color='white')
    
    # Design Move Extraction
    move_box = FancyBboxPatch((4.5, 7.5), 3, 1.5,
                              boxstyle="round,pad=0.1",
                              facecolor=COLORS['secondary'],
                              edgecolor=COLORS['dark'],
                              linewidth=2)
    ax.add_patch(move_box)
    ax.text(6, 8.25, 'DESIGN MOVES', fontsize=12, weight='bold',
            ha='center', va='center', color='white')
    ax.text(6, 7.75, 'Extraction', fontsize=10,
            ha='center', va='center', color='white')
    
    # Semantic Analysis
    semantic_box = FancyBboxPatch((8.5, 7.5), 3, 1.5,
                                  boxstyle="round,pad=0.1",
                                  facecolor=COLORS['accent'],
                                  edgecolor=COLORS['dark'],
                                  linewidth=2)
    ax.add_patch(semantic_box)
    ax.text(10, 8.25, 'SEMANTIC', fontsize=12, weight='bold',
            ha='center', va='center', color='white')
    ax.text(10, 7.75, 'Embeddings', fontsize=10,
            ha='center', va='center', color='white')
    
    # Link Generation
    link_box = FancyBboxPatch((11.5, 7.5), 2, 1.5,
                              boxstyle="round,pad=0.1",
                              facecolor=COLORS['dark'],
                              edgecolor=COLORS['dark'],
                              linewidth=2)
    ax.add_patch(link_box)
    ax.text(12.5, 8.25, 'LINK', fontsize=12, weight='bold',
            ha='center', va='center', color='white')
    ax.text(12.5, 7.75, 'Generation', fontsize=10,
            ha='center', va='center', color='white')
    
    # Analysis Components
    components = [
        ('Pattern\nRecognition', 2, 5, COLORS['primary']),
        ('Critical Moves\nIdentification', 5, 5, COLORS['secondary']),
        ('Phase\nClassification', 8, 5, COLORS['accent']),
        ('Cognitive\nMapping', 11, 5, COLORS['dark'])
    ]
    
    for name, x, y, color in components:
        comp_box = FancyBboxPatch((x-1, y-0.5), 2, 1.2,
                                  boxstyle="round,pad=0.1",
                                  facecolor=color,
                                  edgecolor=COLORS['dark'],
                                  linewidth=1.5, alpha=0.9)
        ax.add_patch(comp_box)
        ax.text(x, y, name, fontsize=10, weight='bold',
                ha='center', va='center', color='white',
                multialignment='center')
    
    # Outputs
    outputs = [
        ('Linkograph\nVisualization', 3, 2.5),
        ('Cognitive\nMetrics', 7, 2.5),
        ('Educational\nInterventions', 11, 2.5)
    ]
    
    for name, x, y in outputs:
        output_box = FancyBboxPatch((x-1.25, y-0.5), 2.5, 1.2,
                                    boxstyle="round,pad=0.1",
                                    facecolor=COLORS['light'],
                                    edgecolor=COLORS['border'],
                                    linewidth=1.5)
        ax.add_patch(output_box)
        ax.text(x, y, name, fontsize=10,
                ha='center', va='center', color=COLORS['text'],
                multialignment='center')
    
    # Arrows
    arrow_props = dict(arrowstyle='->', lw=2, color=COLORS['dark'])
    
    # Horizontal flow
    ax.annotate('', xy=(4.5, 8.25), xytext=(3.5, 8.25),
                arrowprops=arrow_props)
    ax.annotate('', xy=(8.5, 8.25), xytext=(7.5, 8.25),
                arrowprops=arrow_props)
    ax.annotate('', xy=(11.5, 8.25), xytext=(11, 8.25),
                arrowprops=arrow_props)
    
    # To components
    component_arrows = dict(arrowstyle='->', lw=1.5, color=COLORS['border'])
    ax.annotate('', xy=(2, 5.7), xytext=(6, 7.5),
                arrowprops=component_arrows)
    ax.annotate('', xy=(5, 5.7), xytext=(6, 7.5),
                arrowprops=component_arrows)
    ax.annotate('', xy=(8, 5.7), xytext=(10, 7.5),
                arrowprops=component_arrows)
    ax.annotate('', xy=(11, 5.7), xytext=(12.5, 7.5),
                arrowprops=component_arrows)
    
    # To outputs
    ax.annotate('', xy=(3, 3.2), xytext=(2, 4.5),
                arrowprops=component_arrows)
    ax.annotate('', xy=(7, 3.2), xytext=(8, 4.5),
                arrowprops=component_arrows)
    ax.annotate('', xy=(11, 3.2), xytext=(11, 4.5),
                arrowprops=component_arrows)
    
    # Key metrics
    metrics_box = FancyBboxPatch((0.5, 0.5), 13, 1,
                                 boxstyle="round,pad=0.1",
                                 facecolor=COLORS['light'],
                                 edgecolor=COLORS['border'],
                                 linewidth=1)
    ax.add_patch(metrics_box)
    ax.text(7, 1.2, 'KEY METRICS', fontsize=11, weight='bold',
            ha='center', va='center', color=COLORS['dark'])
    ax.text(2, 0.7, 'Link Density', fontsize=9,
            ha='left', va='center', color=COLORS['text'])
    ax.text(5, 0.7, 'Critical Move Ratio', fontsize=9,
            ha='left', va='center', color=COLORS['text'])
    ax.text(8.5, 0.7, 'Phase Balance', fontsize=9,
            ha='left', va='center', color=COLORS['text'])
    ax.text(11.5, 0.7, 'Pattern Frequency', fontsize=9,
            ha='left', va='center', color=COLORS['text'])
    
    plt.tight_layout()
    plt.savefig('linkography_analysis_flow_updated.png', dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    
    print("Created: linkography_analysis_flow_updated.png")

def create_graph_ml_pipeline():
    """Create Graph ML processing pipeline diagram"""
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Title
    ax.text(7, 9.5, 'Graph Machine Learning Pipeline', 
            fontsize=18, weight='bold', ha='center', color=COLORS['dark'])
    
    # Input: Session Data
    input_box = FancyBboxPatch((0.5, 7.5), 2.5, 1.5,
                               boxstyle="round,pad=0.1",
                               facecolor=COLORS['primary'],
                               edgecolor=COLORS['dark'],
                               linewidth=2)
    ax.add_patch(input_box)
    ax.text(1.75, 8.25, 'SESSION', fontsize=12, weight='bold',
            ha='center', va='center', color='white')
    ax.text(1.75, 7.75, 'METRICS', fontsize=12, weight='bold',
            ha='center', va='center', color='white')
    
    # Graph Construction
    graph_box = FancyBboxPatch((3.5, 7.5), 2.5, 1.5,
                               boxstyle="round,pad=0.1",
                               facecolor=COLORS['secondary'],
                               edgecolor=COLORS['dark'],
                               linewidth=2)
    ax.add_patch(graph_box)
    ax.text(4.75, 8.25, 'GRAPH', fontsize=12, weight='bold',
            ha='center', va='center', color='white')
    ax.text(4.75, 7.75, 'BUILDER', fontsize=12, weight='bold',
            ha='center', va='center', color='white')
    
    # Feature Engineering
    feature_box = FancyBboxPatch((6.5, 7.5), 2.5, 1.5,
                                 boxstyle="round,pad=0.1",
                                 facecolor=COLORS['accent'],
                                 edgecolor=COLORS['dark'],
                                 linewidth=2)
    ax.add_patch(feature_box)
    ax.text(7.75, 8.25, 'FEATURE', fontsize=12, weight='bold',
            ha='center', va='center', color='white')
    ax.text(7.75, 7.75, 'EXTRACTION', fontsize=12, weight='bold',
            ha='center', va='center', color='white')
    
    # GNN Processing
    gnn_box = FancyBboxPatch((9.5, 7.5), 2.5, 1.5,
                             boxstyle="round,pad=0.1",
                             facecolor=COLORS['dark'],
                             edgecolor=COLORS['dark'],
                             linewidth=2)
    ax.add_patch(gnn_box)
    ax.text(10.75, 8.25, 'GNN', fontsize=12, weight='bold',
            ha='center', va='center', color='white')
    ax.text(10.75, 7.75, 'MODEL', fontsize=12, weight='bold',
            ha='center', va='center', color='white')
    
    # Predictions
    pred_box = FancyBboxPatch((12.5, 7.5), 1.5, 1.5,
                              boxstyle="round,pad=0.1",
                              facecolor=COLORS['primary'],
                              edgecolor=COLORS['dark'],
                              linewidth=2)
    ax.add_patch(pred_box)
    ax.text(13.25, 8.25, 'PRED', fontsize=12, weight='bold',
            ha='center', va='center', color='white')
    
    # Node Features
    node_features = [
        'Prevention Rate', 'Deep Thinking', 'Response Time', 
        'Question Depth', 'Improvement Score'
    ]
    y_pos = 5.5
    for i, feature in enumerate(node_features):
        feat_box = FancyBboxPatch((0.5 + i*2.5, y_pos-0.4), 2, 0.8,
                                  boxstyle="round,pad=0.05",
                                  facecolor=COLORS['light'],
                                  edgecolor=COLORS['border'],
                                  linewidth=1)
        ax.add_patch(feat_box)
        ax.text(1.5 + i*2.5, y_pos, feature, fontsize=8,
                ha='center', va='center', color=COLORS['text'])
    
    # Edge Types
    edge_types = [
        'Temporal Links', 'Similarity Links', 'Improvement Links'
    ]
    y_pos = 4
    for i, edge_type in enumerate(edge_types):
        edge_box = FancyBboxPatch((2 + i*3.5, y_pos-0.4), 3, 0.8,
                                  boxstyle="round,pad=0.05",
                                  facecolor=COLORS['light'],
                                  edgecolor=COLORS['border'],
                                  linewidth=1)
        ax.add_patch(edge_box)
        ax.text(3.5 + i*3.5, y_pos, edge_type, fontsize=9,
                ha='center', va='center', color=COLORS['text'])
    
    # Model Architecture
    arch_box = FancyBboxPatch((1, 2), 12, 1.5,
                              boxstyle="round,pad=0.1",
                              facecolor=COLORS['light'],
                              edgecolor=COLORS['border'],
                              linewidth=1.5)
    ax.add_patch(arch_box)
    ax.text(7, 3.2, 'GNN ARCHITECTURE', fontsize=11, weight='bold',
            ha='center', va='center', color=COLORS['dark'])
    ax.text(3, 2.7, 'Graph Attention Network (GAT)', fontsize=9,
            ha='left', va='center', color=COLORS['text'])
    ax.text(3, 2.3, '3 Layers, 64 Hidden Units', fontsize=9,
            ha='left', va='center', color=COLORS['text'])
    ax.text(8, 2.7, 'Node Classification Task', fontsize=9,
            ha='left', va='center', color=COLORS['text'])
    ax.text(8, 2.3, 'Proficiency Level Prediction', fontsize=9,
            ha='left', va='center', color=COLORS['text'])
    
    # Outputs
    outputs = [
        ('Session\nClusters', 2, 0.7),
        ('Proficiency\nPredictions', 5, 0.7),
        ('Performance\nPatterns', 8, 0.7),
        ('Anomaly\nDetection', 11, 0.7)
    ]
    
    for name, x, y in outputs:
        out_box = FancyBboxPatch((x-0.75, y-0.35), 1.5, 0.7,
                                 boxstyle="round,pad=0.05",
                                 facecolor=COLORS['secondary'],
                                 edgecolor=COLORS['dark'],
                                 linewidth=1, alpha=0.8)
        ax.add_patch(out_box)
        ax.text(x, y, name, fontsize=8,
                ha='center', va='center', color='white',
                multialignment='center')
    
    # Arrows
    arrow_props = dict(arrowstyle='->', lw=2, color=COLORS['dark'])
    
    # Main flow
    ax.annotate('', xy=(3.5, 8.25), xytext=(3, 8.25),
                arrowprops=arrow_props)
    ax.annotate('', xy=(6.5, 8.25), xytext=(6, 8.25),
                arrowprops=arrow_props)
    ax.annotate('', xy=(9.5, 8.25), xytext=(9, 8.25),
                arrowprops=arrow_props)
    ax.annotate('', xy=(12.5, 8.25), xytext=(12, 8.25),
                arrowprops=arrow_props)
    
    # To features/edges
    feature_arrows = dict(arrowstyle='->', lw=1.5, color=COLORS['border'])
    ax.annotate('', xy=(4.75, 6.3), xytext=(4.75, 7.5),
                arrowprops=feature_arrows)
    ax.annotate('', xy=(7.75, 4.8), xytext=(7.75, 7.5),
                arrowprops=feature_arrows)
    
    # To outputs
    ax.annotate('', xy=(7, 1.5), xytext=(10.75, 7.5),
                arrowprops=feature_arrows)
    
    plt.tight_layout()
    plt.savefig('graph_ml_pipeline_updated.png', dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    
    print("Created: graph_ml_pipeline_updated.png")

def create_dashboard_architecture():
    """Create dashboard architecture diagram"""
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Title
    ax.text(7, 9.5, 'Benchmarking Dashboard Architecture', 
            fontsize=18, weight='bold', ha='center', color=COLORS['dark'])
    
    # Main Dashboard Container
    main_box = FancyBboxPatch((0.5, 7), 13, 2,
                              boxstyle="round,pad=0.1",
                              facecolor=COLORS['primary'],
                              edgecolor=COLORS['dark'],
                              linewidth=2.5, alpha=0.9)
    ax.add_patch(main_box)
    ax.text(7, 8.3, 'BENCHMARKING DASHBOARD', fontsize=16, weight='bold',
            ha='center', va='center', color='white')
    ax.text(7, 7.7, 'benchmark_dashboard.py', fontsize=11,
            ha='center', va='center', color='white')
    
    # Navigation Sections
    sections = [
        ('Overview', 1.5, 5.5),
        ('Cognitive\nAssessment', 3.5, 5.5),
        ('Linkography', 5.5, 5.5),
        ('Graph ML', 7.5, 5.5),
        ('Comparative\nAnalysis', 9.5, 5.5),
        ('Export\nOptions', 11.5, 5.5),
        ('Technical\nDetails', 13, 5.5)
    ]
    
    for name, x, y in sections:
        section_box = FancyBboxPatch((x-0.65, y-0.5), 1.3, 1,
                                     boxstyle="round,pad=0.05",
                                     facecolor=COLORS['secondary'],
                                     edgecolor=COLORS['dark'],
                                     linewidth=1.5, alpha=0.9)
        ax.add_patch(section_box)
        ax.text(x, y, name, fontsize=8, weight='bold',
                ha='center', va='center', color='white',
                multialignment='center')
    
    # Data Sources
    data_sources = [
        ('Master Session\nMetrics CSV', 2, 3.5, COLORS['accent']),
        ('Aggregate\nMetrics CSV', 5, 3.5, COLORS['accent']),
        ('Benchmark\nReport JSON', 8, 3.5, COLORS['accent']),
        ('Evaluation\nReports', 11, 3.5, COLORS['accent'])
    ]
    
    for name, x, y, color in data_sources:
        data_box = FancyBboxPatch((x-1, y-0.5), 2, 1,
                                  boxstyle="round,pad=0.1",
                                  facecolor=color,
                                  edgecolor=COLORS['dark'],
                                  linewidth=1.5, alpha=0.8)
        ax.add_patch(data_box)
        ax.text(x, y, name, fontsize=9, weight='bold',
                ha='center', va='center', color='white',
                multialignment='center')
    
    # Visualization Components
    viz_components = [
        ('Plotly\nCharts', 2, 1.5),
        ('PyVis\nGraphs', 4.5, 1.5),
        ('Streamlit\nMetrics', 7, 1.5),
        ('HTML\nReports', 9.5, 1.5),
        ('CSV/JSON\nExports', 12, 1.5)
    ]
    
    for name, x, y in viz_components:
        viz_box = FancyBboxPatch((x-0.75, y-0.4), 1.5, 0.8,
                                 boxstyle="round,pad=0.05",
                                 facecolor=COLORS['light'],
                                 edgecolor=COLORS['border'],
                                 linewidth=1)
        ax.add_patch(viz_box)
        ax.text(x, y, name, fontsize=8,
                ha='center', va='center', color=COLORS['text'],
                multialignment='center')
    
    # Arrows
    arrow_props = dict(arrowstyle='->', lw=1.5, color=COLORS['border'])
    
    # From main to sections
    for x in [1.5, 3.5, 5.5, 7.5, 9.5, 11.5, 13]:
        ax.annotate('', xy=(x, 6), xytext=(7, 7),
                    arrowprops=arrow_props)
    
    # From data sources to dashboard
    for x in [2, 5, 8, 11]:
        ax.annotate('', xy=(x, 4), xytext=(x, 5),
                    arrowprops=arrow_props)
    
    # To visualization components
    for x in [2, 4.5, 7, 9.5, 12]:
        ax.annotate('', xy=(x, 1.9), xytext=(x, 3),
                    arrowprops=arrow_props)
    
    # Key Features Box
    features_box = FancyBboxPatch((0.5, 0.2), 13, 0.6,
                                  boxstyle="round,pad=0.05",
                                  facecolor=COLORS['light'],
                                  edgecolor=COLORS['border'],
                                  linewidth=1)
    ax.add_patch(features_box)
    ax.text(7, 0.5, 'Real-time Updates | Interactive Visualizations | Professional Export | No Hardcoded Values',
            fontsize=10, ha='center', va='center', color=COLORS['text'], weight='bold')
    
    plt.tight_layout()
    plt.savefig('dashboard_architecture_updated.png', dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    
    print("Created: dashboard_architecture_updated.png")

def create_export_system_flow():
    """Create export system flow diagram"""
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.axis('off')
    
    # Title
    ax.text(6, 7.5, 'Export System Architecture', 
            fontsize=18, weight='bold', ha='center', color=COLORS['dark'])
    
    # Export Options Selection
    selection_box = FancyBboxPatch((0.5, 5.5), 3, 1.5,
                                   boxstyle="round,pad=0.1",
                                   facecolor=COLORS['primary'],
                                   edgecolor=COLORS['dark'],
                                   linewidth=2)
    ax.add_patch(selection_box)
    ax.text(2, 6.25, 'EXPORT OPTIONS', fontsize=12, weight='bold',
            ha='center', va='center', color='white')
    
    # Report Types
    report_types = [
        ('Comparative\nAnalysis', 1, 4),
        ('Group\nAnalysis', 3, 4),
        ('Session\nAnalysis', 5, 4),
        ('Full\nBenchmark', 7, 4)
    ]
    
    for name, x, y in report_types:
        type_box = FancyBboxPatch((x-0.65, y-0.4), 1.3, 0.8,
                                  boxstyle="round,pad=0.05",
                                  facecolor=COLORS['secondary'],
                                  edgecolor=COLORS['dark'],
                                  linewidth=1, alpha=0.9)
        ax.add_patch(type_box)
        ax.text(x, y, name, fontsize=8,
                ha='center', va='center', color='white',
                multialignment='center')
    
    # Processing Components
    components = [
        ('Simple Report\nGenerator', 2, 2.5, COLORS['accent']),
        ('Insights\nGenerator', 4.5, 2.5, COLORS['accent']),
        ('Visualization\nEngine', 7, 2.5, COLORS['accent']),
        ('Data\nProcessor', 9.5, 2.5, COLORS['accent'])
    ]
    
    for name, x, y, color in components:
        comp_box = FancyBboxPatch((x-0.85, y-0.5), 1.7, 1,
                                  boxstyle="round,pad=0.1",
                                  facecolor=color,
                                  edgecolor=COLORS['dark'],
                                  linewidth=1.5, alpha=0.9)
        ax.add_patch(comp_box)
        ax.text(x, y, name, fontsize=9, weight='bold',
                ha='center', va='center', color='white',
                multialignment='center')
    
    # Export Formats
    formats = [
        ('HTML\nReport', 3, 0.8),
        ('JSON\nData', 6, 0.8),
        ('CSV\nTables', 9, 0.8)
    ]
    
    for name, x, y in formats:
        format_box = FancyBboxPatch((x-0.75, y-0.4), 1.5, 0.8,
                                    boxstyle="round,pad=0.05",
                                    facecolor=COLORS['dark'],
                                    edgecolor=COLORS['dark'],
                                    linewidth=1.5)
        ax.add_patch(format_box)
        ax.text(x, y, name, fontsize=9, weight='bold',
                ha='center', va='center', color='white',
                multialignment='center')
    
    # Arrows
    arrow_props = dict(arrowstyle='->', lw=1.5, color=COLORS['border'])
    
    # From selection to report types
    for x in [1, 3, 5, 7]:
        ax.annotate('', xy=(x, 4.4), xytext=(2, 5.5),
                    arrowprops=arrow_props)
    
    # From report types to components
    for x in [2, 4.5, 7, 9.5]:
        ax.annotate('', xy=(x, 3), xytext=(4, 3.6),
                    arrowprops=arrow_props)
    
    # From components to formats
    ax.annotate('', xy=(3, 1.2), xytext=(2, 2),
                arrowprops=arrow_props)
    ax.annotate('', xy=(6, 1.2), xytext=(4.5, 2),
                arrowprops=arrow_props)
    ax.annotate('', xy=(9, 1.2), xytext=(9.5, 2),
                arrowprops=arrow_props)
    
    # Feature note
    feature_box = FancyBboxPatch((8.5, 5.5), 3, 1.5,
                                 boxstyle="round,pad=0.1",
                                 facecolor=COLORS['light'],
                                 edgecolor=COLORS['border'],
                                 linewidth=1.5)
    ax.add_patch(feature_box)
    ax.text(10, 6.7, 'NO WEASYPRINT', fontsize=10, weight='bold',
            ha='center', va='center', color=COLORS['dark'])
    ax.text(10, 6.3, 'Simple HTML', fontsize=9,
            ha='center', va='center', color=COLORS['text'])
    ax.text(10, 5.9, 'Beautiful Reports', fontsize=9,
            ha='center', va='center', color=COLORS['text'])
    ax.text(10, 5.5, 'Zero Dependencies', fontsize=9,
            ha='center', va='center', color=COLORS['text'])
    
    plt.tight_layout()
    plt.savefig('export_system_flow.png', dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    
    print("Created: export_system_flow.png")

# Run all diagram creation functions
if __name__ == "__main__":
    print("Updating all benchmarking diagrams...")
    
    create_comprehensive_data_flow()
    create_metric_calculation_flow()
    create_linkography_analysis_flow()
    create_graph_ml_pipeline()
    create_dashboard_architecture()
    create_export_system_flow()
    
    print("\nAll diagrams updated successfully!")
    print("\nDiagrams created:")
    print("- comprehensive_data_flow.png")
    print("- metric_calculation_flow_updated.png")
    print("- linkography_analysis_flow_updated.png")
    print("- graph_ml_pipeline_updated.png")
    print("- dashboard_architecture_updated.png")
    print("- export_system_flow.png")