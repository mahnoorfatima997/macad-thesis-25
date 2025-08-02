"""
Generate a visual diagram of the dashboard structure and features
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle, FancyArrowPatch
import matplotlib.lines as mlines
from thesis_colors import THESIS_COLORS, METRIC_COLORS, COLOR_GRADIENTS

def create_dashboard_structure_diagram():
    """Create a hierarchical diagram of dashboard sections and features"""
    
    fig = plt.figure(figsize=(20, 14))
    ax = fig.add_subplot(111)
    
    # Title
    ax.text(10, 13, 'MEGA Dashboard Structure & Features', 
            fontsize=20, fontweight='bold', ha='center')
    
    # Main dashboard box
    main_box = FancyBboxPatch((0.5, 10.5), 19, 1.5,
                             boxstyle="round,pad=0.1",
                             facecolor=THESIS_COLORS['primary_dark'],
                             edgecolor='black', linewidth=3)
    ax.add_patch(main_box)
    ax.text(10, 11.25, 'MEGA Benchmarking Dashboard', 
            ha='center', va='center', fontsize=14, fontweight='bold', color='white')
    
    # Define sections with their subsections and key features
    sections = [
        {
            'name': 'Overview',
            'pos': (1, 8),
            'color': THESIS_COLORS['neutral_warm'],
            'subsections': [
                'Key Metrics Panel\n• Total Sessions\n• Avg Prevention\n• Avg Deep Thinking\n• Overall Improvement',
                'Learning Metrics Chart\n• Time Series Plot\n• Multi-line Trends',
                'Proficiency Distribution\n• Pie Chart\n• K-means Clustering'
            ]
        },
        {
            'name': 'Cognitive\nPatterns',
            'pos': (4.5, 8),
            'color': THESIS_COLORS['primary_pink'],
            'subsections': [
                'Session Comparison\n• Detailed Table\n• All Metrics',
                'Average Patterns\n• Radar Chart\n• Baseline Overlay',
                'Temporal Analysis\n• Trend Detection'
            ]
        },
        {
            'name': 'Learning\nProgression',
            'pos': (8, 8),
            'color': THESIS_COLORS['primary_rose'],
            'subsections': [
                'Skill Tracking\n• Level Changes\n• Progression Score',
                'Learning Velocity\n• Rate Analysis\n• Acceleration',
                'Milestone Tracking\n• Achievements'
            ]
        },
        {
            'name': 'Agent\nPerformance',
            'pos': (11.5, 8),
            'color': THESIS_COLORS['primary_violet'],
            'subsections': [
                'Usage Distribution\n• Bar Chart\n• Frequency Analysis',
                'Effectiveness\n• Per-Agent Metrics\n• Quality Scores',
                'Handoff Flow\n• Sankey Diagram\n• Transitions'
            ]
        },
        {
            'name': 'Comparative\nAnalysis',
            'pos': (15, 8),
            'color': THESIS_COLORS['primary_purple'],
            'subsections': [
                'Improvement Dims\n• Pre/Post Compare\n• % Changes',
                'Feature Impact\n• Correlation Analysis\n• Real-time Calc',
                'Baseline Compare\n• Literature Values'
            ]
        },
        {
            'name': 'Anthropomorphism\nAnalysis',
            'pos': (18.5, 8),
            'color': THESIS_COLORS['accent_coral'],
            'subsections': [
                'CAI Score\n• Autonomy Index\n• Dependency Ratio',
                'ADS Score\n• Personal Attributions\n• Emotional Language',
                'PBI & NES\n• Boundaries\n• Engagement'
            ]
        },
        {
            'name': 'Linkography\nAnalysis',
            'pos': (3, 3.5),
            'color': THESIS_COLORS['neutral_orange'],
            'subsections': [
                'Design Moves\n• Extraction\n• Classification',
                'Link Generation\n• Fuzzy Links\n• Similarity > 0.65',
                'Metrics & Patterns\n• Link Density\n• Critical Moves'
            ]
        },
        {
            'name': 'Proficiency\nAnalysis',
            'pos': (8, 3.5),
            'color': THESIS_COLORS['neutral_warm'],
            'subsections': [
                'Characteristics\n• Question Quality\n• Reflection Depth',
                'Skill Metrics\n• Integration\n• Problem Solving',
                'Growth Potential\n• Trend Analysis\n• Barriers'
            ]
        },
        {
            'name': 'Graph ML\nAnalysis',
            'pos': (13, 3.5),
            'color': THESIS_COLORS['primary_dark'],
            'subsections': [
                'Graph Construction\n• Nodes & Edges\n• Embeddings',
                'GNN Processing\n• GraphSAGE\n• Neighborhoods',
                'Clustering\n• K-means\n• Proficiency Groups'
            ]
        }
    ]
    
    # Draw sections
    for section in sections:
        # Section header
        section_box = FancyBboxPatch((section['pos'][0]-1.3, section['pos'][1]-0.4), 
                                    2.6, 0.8,
                                    boxstyle="round,pad=0.05",
                                    facecolor=section['color'],
                                    edgecolor='black', linewidth=2)
        ax.add_patch(section_box)
        
        # Determine text color based on background
        text_color = 'white' if section['name'] in ['Agent\nPerformance', 'Comparative\nAnalysis', 
                                                    'Graph ML\nAnalysis', 'Anthropomorphism\nAnalysis'] else 'black'
        ax.text(section['pos'][0], section['pos'][1], section['name'],
                ha='center', va='center', fontsize=10, fontweight='bold', color=text_color)
        
        # Connection from main dashboard
        if section['pos'][1] > 5:  # Upper row
            arrow = FancyArrowPatch((section['pos'][0], 10.5), 
                                   (section['pos'][0], section['pos'][1] + 0.4),
                                   arrowstyle='->', mutation_scale=15,
                                   color='gray', linewidth=1.5, alpha=0.7)
            ax.add_patch(arrow)
        
        # Subsections
        subsection_y = section['pos'][1] - 1.5
        for i, subsection in enumerate(section['subsections']):
            sub_box = FancyBboxPatch((section['pos'][0]-1.3, subsection_y - i*1.2 - 0.5), 
                                    2.6, 1.0,
                                    boxstyle="round,pad=0.05",
                                    facecolor='white',
                                    edgecolor=section['color'], linewidth=1.5, alpha=0.9)
            ax.add_patch(sub_box)
            ax.text(section['pos'][0], subsection_y - i*1.2, subsection,
                    ha='center', va='center', fontsize=7, multialignment='center')
    
    # Add data flow indicators
    # From Overview to other sections
    for target_x in [4.5, 8, 11.5, 15]:
        arrow = FancyArrowPatch((2.3, 7), (target_x-1.3, 7),
                               arrowstyle='->', mutation_scale=10,
                               color='lightgray', linewidth=1, linestyle='dashed', alpha=0.5)
        ax.add_patch(arrow)
    
    # Add theoretical foundation boxes
    theory_y = 0.5
    theories = [
        ("Bloom's Taxonomy", THESIS_COLORS['primary_purple']),
        ("Vygotsky's ZPD", THESIS_COLORS['primary_violet']),
        ("Goldschmidt's Linkography", THESIS_COLORS['neutral_orange']),
        ("Self-Determination Theory", THESIS_COLORS['primary_rose']),
        ("Graph Neural Networks", THESIS_COLORS['primary_dark'])
    ]
    
    for i, (theory, color) in enumerate(theories):
        theory_box = Rectangle((1 + i*3.8, theory_y), 3.6, 0.6,
                              facecolor=color, edgecolor='black', linewidth=1, alpha=0.7)
        ax.add_patch(theory_box)
        text_color = 'white' if theory == "Graph Neural Networks" else 'black'
        ax.text(2.8 + i*3.8, theory_y + 0.3, theory, 
                ha='center', va='center', fontsize=8, style='italic', color=text_color)
    
    # Add metrics summary on the right
    metrics_box = FancyBboxPatch((16, 0.2), 3.5, 2.5,
                                boxstyle="round,pad=0.1",
                                facecolor=THESIS_COLORS['neutral_light'],
                                edgecolor='black', linewidth=2)
    ax.add_patch(metrics_box)
    ax.text(17.75, 2.4, 'Key Metrics', ha='center', fontweight='bold', fontsize=10)
    
    key_metrics = [
        '• 30+ Individual Features',
        '• 9 Main Sections',
        '• 4 Core Cognitive Metrics',
        '• 5 Theoretical Frameworks',
        '• Real-time Calculations',
        '• Interactive Visualizations'
    ]
    
    for i, metric in enumerate(key_metrics):
        ax.text(16.2, 2.0 - i*0.25, metric, fontsize=8)
    
    # Legend for feature types
    legend_elements = [
        mpatches.Patch(color=THESIS_COLORS['primary_purple'], label='Metric'),
        mpatches.Patch(color=THESIS_COLORS['accent_coral'], label='Visualization'),
        mpatches.Patch(color=THESIS_COLORS['primary_dark'], label='Analysis'),
        mpatches.Patch(color=THESIS_COLORS['neutral_orange'], label='Process')
    ]
    ax.legend(handles=legend_elements, loc='lower left', fontsize=8)
    
    ax.set_xlim(-0.5, 20.5)
    ax.set_ylim(0, 14)
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('dashboard_structure_diagram.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

def create_feature_type_breakdown():
    """Create a breakdown chart of feature types"""
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Feature type distribution
    feature_types = ['Metric', 'Visualization', 'Analysis', 'Process', 'Table', 'Algorithm', 'Model', 'Reference']
    feature_counts = [11, 10, 5, 3, 1, 2, 1, 1]  # Based on actual counts
    colors = [THESIS_COLORS['primary_purple'], THESIS_COLORS['accent_coral'], 
              THESIS_COLORS['primary_dark'], THESIS_COLORS['neutral_orange'],
              THESIS_COLORS['neutral_warm'], THESIS_COLORS['primary_violet'],
              THESIS_COLORS['primary_rose'], THESIS_COLORS['primary_pink']]
    
    # Pie chart
    wedges, texts, autotexts = ax1.pie(feature_counts, labels=feature_types, colors=colors, 
                                       autopct='%1.1f%%', startangle=90)
    ax1.set_title('Feature Type Distribution', fontsize=14, fontweight='bold')
    
    # Section distribution
    sections = ['Overview', 'Cognitive\nPatterns', 'Learning\nProgression', 'Agent\nPerformance', 
                'Comparative\nAnalysis', 'Anthropomorphism', 'Linkography', 'Proficiency', 'Graph ML']
    section_counts = [6, 3, 2, 3, 2, 4, 4, 3, 3]  # Based on main features per section
    
    bars = ax2.bar(range(len(sections)), section_counts, color=COLOR_GRADIENTS['cognitive_scale'])
    ax2.set_xticks(range(len(sections)))
    ax2.set_xticklabels(sections, rotation=45, ha='right', fontsize=8)
    ax2.set_ylabel('Number of Features')
    ax2.set_title('Features per Dashboard Section', fontsize=14, fontweight='bold')
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}', ha='center', va='bottom', fontsize=9)
    
    plt.suptitle('Dashboard Feature Analysis', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig('dashboard_feature_breakdown.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

if __name__ == "__main__":
    print("Generating dashboard structure diagram...")
    create_dashboard_structure_diagram()
    print("Created dashboard_structure_diagram.png")
    
    print("Generating feature breakdown charts...")
    create_feature_type_breakdown()
    print("Created dashboard_feature_breakdown.png")