"""
Comparative Analysis Framework Diagram Generator
Creates visual representation of the 3-group comparison methodology
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Rectangle, Polygon, Wedge
import numpy as np
import os
import sys

# Add the benchmarking directory to the path to import thesis colors
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'benchmarking'))
from thesis_colors import THESIS_COLORS, METRIC_COLORS, UI_COLORS

def create_comparative_framework_diagram():
    """Create comprehensive 3-group comparative analysis framework"""
    
    # Create figure with proper sizing
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(18, 14))
    
    # Remove individual subplot titles and use the main title
    fig.suptitle('MEGA Architectural Mentor - Comparative Analysis Framework', 
                fontsize=18, fontweight='bold', color=THESIS_COLORS['primary_dark'], y=0.95)
    
    # ===== TOP LEFT: THREE EXPERIMENTAL GROUPS =====
    
    groups = {
        'mentor': {
            'pos': (1, 2), 'size': (2, 1.5),
            'color': THESIS_COLORS['primary_dark'],
            'title': 'MENTOR Group',
            'description': 'Multi-Agent\nEducational System',
            'features': [
                '• Socratic Questioning',
                '• Adaptive Scaffolding', 
                '• Cognitive Enhancement',
                '• Real-time Assessment',
                '• Personalized Learning'
            ]
        },
        'generic_ai': {
            'pos': (4, 2), 'size': (2, 1.5),
            'color': THESIS_COLORS['neutral_orange'],
            'title': 'Generic AI Group',
            'description': 'Standard AI\nAssistant',
            'features': [
                '• Direct Answers',
                '• Information Retrieval',
                '• Basic Q&A Format',
                '• No Scaffolding',
                '• Reactive Responses'
            ]
        },
        'control': {
            'pos': (7, 2), 'size': (2, 1.5),
            'color': THESIS_COLORS['accent_coral'],
            'title': 'Control Group',
            'description': 'Traditional\nResearch Methods',
            'features': [
                '• Independent Research',
                '• Library Resources',
                '• Self-directed Learning',
                '• No AI Assistance',
                '• Manual Documentation'
            ]
        }
    }
    
    # Draw groups
    for group_key, group in groups.items():
        x, y = group['pos']
        width, height = group['size']
        
        # Main group box
        box = FancyBboxPatch(
            (x - width/2, y - height/2), width, height,
            boxstyle="round,pad=0.1",
            facecolor=group['color'], edgecolor='white', linewidth=3, alpha=0.85
        )
        ax1.add_patch(box)
        
        # Title
        ax1.text(x, y + 0.5, group['title'], ha='center', va='center',
                fontsize=12, fontweight='bold', color='white')
        
        # Description
        ax1.text(x, y + 0.1, group['description'], ha='center', va='center',
                fontsize=10, color='white', style='italic')
        
        # Features (in smaller text box below)
        feature_box = FancyBboxPatch(
            (x - width/2 + 0.1, y - height/2 - 0.8), width - 0.2, 0.7,
            boxstyle="round,pad=0.05",
            facecolor=THESIS_COLORS['neutral_light'], 
            edgecolor=group['color'], linewidth=2, alpha=0.9
        )
        ax1.add_patch(feature_box)
        
        features_text = '\n'.join(group['features'])
        ax1.text(x, y - height/2 - 0.45, features_text, ha='center', va='center',
                fontsize=8, color=THESIS_COLORS['primary_dark'])
    
    # Add arrows showing comparison direction
    comparison_arrows = [
        (groups['mentor']['pos'], groups['generic_ai']['pos']),
        (groups['generic_ai']['pos'], groups['control']['pos']),
        (groups['mentor']['pos'], groups['control']['pos'])
    ]
    
    for start_pos, end_pos in comparison_arrows:
        arrow = FancyArrowPatch(
            start_pos, end_pos,
            arrowstyle='<->', mutation_scale=15,
            color=THESIS_COLORS['primary_purple'], linewidth=2, alpha=0.6,
            connectionstyle="arc3,rad=0.2"
        )
        ax1.add_patch(arrow)
    
    ax1.text(4, 3.5, 'Three-Group Experimental Design', ha='center', va='center',
            fontsize=14, fontweight='bold', color=THESIS_COLORS['primary_dark'])
    
    ax1.set_xlim(-0.5, 8.5)
    ax1.set_ylim(-0.5, 4)
    ax1.set_aspect('equal')
    ax1.axis('off')
    
    # ===== TOP RIGHT: MEASUREMENT DIMENSIONS =====
    
    dimensions = [
        {'name': 'Cognitive Metrics', 'value': 0.85, 'color': THESIS_COLORS['primary_violet']},
        {'name': 'Learning Progression', 'value': 0.72, 'color': THESIS_COLORS['primary_rose']},
        {'name': 'Knowledge Integration', 'value': 0.68, 'color': THESIS_COLORS['neutral_warm']},
        {'name': 'Design Quality', 'value': 0.78, 'color': THESIS_COLORS['accent_magenta']},
        {'name': 'Time Efficiency', 'value': 0.65, 'color': THESIS_COLORS['neutral_orange']},
        {'name': 'Engagement Level', 'value': 0.82, 'color': THESIS_COLORS['primary_pink']}
    ]
    
    # Radar chart for dimensions
    angles = np.linspace(0, 2 * np.pi, len(dimensions), endpoint=False)
    angles = np.concatenate((angles, [angles[0]]))  # Close the plot
    
    # MENTOR group performance (example data)
    mentor_values = [dim['value'] for dim in dimensions] + [dimensions[0]['value']]
    generic_ai_values = [dim['value'] * 0.6 for dim in dimensions] + [dimensions[0]['value'] * 0.6]
    control_values = [dim['value'] * 0.4 for dim in dimensions] + [dimensions[0]['value'] * 0.4]
    
    ax2.plot(angles, mentor_values, 'o-', linewidth=3, label='MENTOR', 
            color=THESIS_COLORS['primary_dark'], alpha=0.8, markersize=6)
    ax2.fill(angles, mentor_values, alpha=0.25, color=THESIS_COLORS['primary_dark'])
    
    ax2.plot(angles, generic_ai_values, 's-', linewidth=3, label='Generic AI',
            color=THESIS_COLORS['neutral_orange'], alpha=0.8, markersize=6)
    ax2.fill(angles, generic_ai_values, alpha=0.25, color=THESIS_COLORS['neutral_orange'])
    
    ax2.plot(angles, control_values, '^-', linewidth=3, label='Control',
            color=THESIS_COLORS['accent_coral'], alpha=0.8, markersize=6)
    ax2.fill(angles, control_values, alpha=0.25, color=THESIS_COLORS['accent_coral'])
    
    # Add dimension labels
    ax2.set_xticks(angles[:-1])
    ax2.set_xticklabels([dim['name'] for dim in dimensions], fontsize=10, 
                       color=THESIS_COLORS['primary_dark'], fontweight='bold')
    ax2.set_ylim(0, 1)
    ax2.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax2.set_yticklabels(['20%', '40%', '60%', '80%', '100%'], fontsize=8)
    ax2.grid(True, alpha=0.3)
    ax2.set_title('Comparative Performance Across Dimensions', fontsize=12, 
                 fontweight='bold', color=THESIS_COLORS['primary_dark'], pad=20)
    ax2.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
    
    # ===== BOTTOM LEFT: STATISTICAL ANALYSIS METHODS =====
    
    statistical_methods = {
        'anova': {
            'pos': (1, 3), 'size': (1.8, 0.8),
            'color': THESIS_COLORS['primary_violet'],
            'text': 'ANOVA\nF-test',
            'purpose': 'Group Differences'
        },
        'tukey': {
            'pos': (3.5, 3), 'size': (1.8, 0.8),
            'color': THESIS_COLORS['primary_rose'],
            'text': 'Tukey HSD\nPost-hoc',
            'purpose': 'Pairwise Comparisons'
        },
        'effect_size': {
            'pos': (6, 3), 'size': (1.8, 0.8),
            'color': THESIS_COLORS['accent_magenta'],
            'text': 'Cohen\'s d\nEffect Size',
            'purpose': 'Practical Significance'
        },
        'regression': {
            'pos': (2.25, 1.5), 'size': (1.8, 0.8),
            'color': THESIS_COLORS['neutral_warm'],
            'text': 'Linear\nRegression',
            'purpose': 'Trend Analysis'
        },
        'correlation': {
            'pos': (4.75, 1.5), 'size': (1.8, 0.8),
            'color': THESIS_COLORS['primary_pink'],
            'text': 'Correlation\nAnalysis',
            'purpose': 'Relationship Strength'
        }
    }
    
    for method_key, method in statistical_methods.items():
        x, y = method['pos']
        width, height = method['size']
        
        # Method box
        box = FancyBboxPatch(
            (x - width/2, y - height/2), width, height,
            boxstyle="round,pad=0.1",
            facecolor=method['color'], edgecolor='white', linewidth=2, alpha=0.8
        )
        ax3.add_patch(box)
        
        # Method text
        ax3.text(x, y + 0.1, method['text'], ha='center', va='center',
                fontsize=10, fontweight='bold', color='white')
        
        # Purpose
        ax3.text(x, y - 0.2, method['purpose'], ha='center', va='center',
                fontsize=8, color='white', style='italic')
    
    # Add statistical workflow arrows
    workflow_connections = [
        ('anova', 'tukey'),
        ('tukey', 'effect_size'),
        ('anova', 'regression'),
        ('regression', 'correlation')
    ]
    
    for start, end in workflow_connections:
        start_pos = statistical_methods[start]['pos']
        end_pos = statistical_methods[end]['pos']
        
        arrow = FancyArrowPatch(
            start_pos, end_pos,
            arrowstyle='->', mutation_scale=12,
            color=THESIS_COLORS['primary_dark'], linewidth=2, alpha=0.6
        )
        ax3.add_patch(arrow)
    
    ax3.text(3.5, 4, 'Statistical Analysis Pipeline', ha='center', va='center',
            fontsize=14, fontweight='bold', color=THESIS_COLORS['primary_dark'])
    
    ax3.set_xlim(0, 7)
    ax3.set_ylim(0.5, 4.5)
    ax3.set_aspect('equal')
    ax3.axis('off')
    
    # ===== BOTTOM RIGHT: OUTCOME MEASURES =====
    
    # Create a comprehensive outcomes visualization
    outcome_categories = {
        'learning_outcomes': {
            'metrics': ['Knowledge Retention', 'Skill Development', 'Conceptual Understanding'],
            'values': [0.82, 0.75, 0.88],
            'color': THESIS_COLORS['primary_violet']
        },
        'cognitive_benefits': {
            'metrics': ['Critical Thinking', 'Problem Solving', 'Metacognition'],
            'values': [0.78, 0.71, 0.65],
            'color': THESIS_COLORS['primary_rose']
        },
        'engagement_measures': {
            'metrics': ['Active Participation', 'Time on Task', 'Question Quality'],
            'values': [0.85, 0.69, 0.72],
            'color': THESIS_COLORS['accent_magenta']
        },
        'efficiency_metrics': {
            'metrics': ['Task Completion', 'Resource Utilization', 'Error Reduction'],
            'values': [0.74, 0.81, 0.67],
            'color': THESIS_COLORS['neutral_warm']
        }
    }
    
    # Stacked horizontal bar chart
    category_names = list(outcome_categories.keys())
    y_positions = np.arange(len(category_names))
    
    bar_height = 0.6
    colors = [outcome_categories[cat]['color'] for cat in category_names]
    
    # Calculate average values for each category
    avg_values = [np.mean(outcome_categories[cat]['values']) for cat in category_names]
    
    bars = ax4.barh(y_positions, avg_values, height=bar_height, 
                   color=colors, alpha=0.8, edgecolor='white', linewidth=2)
    
    # Add value labels
    for i, (cat_name, avg_val) in enumerate(zip(category_names, avg_values)):
        ax4.text(avg_val + 0.02, i, f'{avg_val:.2f}', va='center', ha='left',
                fontweight='bold', fontsize=10, color=THESIS_COLORS['primary_dark'])
        
        # Add individual metric details
        metrics_text = ' • '.join(outcome_categories[cat_name]['metrics'])
        ax4.text(0.02, i - 0.15, metrics_text, va='center', ha='left',
                fontsize=8, color=THESIS_COLORS['primary_dark'], style='italic')
    
    ax4.set_yticks(y_positions)
    ax4.set_yticklabels([cat.replace('_', ' ').title() for cat in category_names], 
                       fontsize=10, color=THESIS_COLORS['primary_dark'], fontweight='bold')
    ax4.set_xlabel('Average Performance Score', fontweight='bold', 
                  color=THESIS_COLORS['primary_dark'])
    ax4.set_xlim(0, 1)
    ax4.set_title('Comprehensive Outcome Measures', fontsize=12, 
                 fontweight='bold', color=THESIS_COLORS['primary_dark'])
    ax4.grid(axis='x', alpha=0.3)
    
    # Add significance indicators
    significance_levels = ['***', '**', '*', 'ns']
    sig_colors = [THESIS_COLORS['primary_dark'], THESIS_COLORS['primary_violet'], 
                  THESIS_COLORS['neutral_orange'], THESIS_COLORS['accent_coral']]
    
    for i, (sig, color) in enumerate(zip(significance_levels, sig_colors)):
        y_pos = len(category_names) - 1 - i
        ax4.text(0.95, y_pos, sig, va='center', ha='center',
                fontsize=12, fontweight='bold', color=color,
                bbox=dict(boxstyle="circle,pad=0.1", facecolor='white', edgecolor=color))
    
    plt.tight_layout()
    return fig

def save_diagram():
    """Save the diagram in multiple formats"""
    fig = create_comparative_framework_diagram()
    
    # Define output paths
    base_path = os.path.dirname(__file__)
    png_path = os.path.join(base_path, '07_comparative_framework.png')
    svg_path = os.path.join(base_path, '07_comparative_framework.svg')
    
    # Save as PNG with high DPI
    fig.savefig(png_path, dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    
    # Save as SVG for scalability
    fig.savefig(svg_path, format='svg', bbox_inches='tight',
                facecolor='white', edgecolor='none')
    
    print(f"Comparative Framework diagram saved:")
    print(f"  PNG: {png_path}")
    print(f"  SVG: {svg_path}")
    
    plt.close(fig)

if __name__ == "__main__":
    save_diagram()