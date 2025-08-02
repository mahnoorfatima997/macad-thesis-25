"""
Generate a visual reference for the thesis color palette
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from thesis_colors import THESIS_COLORS, METRIC_COLORS, COLOR_GRADIENTS

def create_color_palette_reference():
    """Create a visual reference showing all thesis colors"""
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10))
    
    # Main thesis colors
    ax1.set_title('Main Thesis Colors', fontsize=14, fontweight='bold')
    colors = list(THESIS_COLORS.items())
    n_colors = len(colors)
    
    for i, (name, color) in enumerate(colors):
        # Color swatch
        rect = mpatches.Rectangle((i, 0), 1, 1, facecolor=color, edgecolor='black', linewidth=1)
        ax1.add_patch(rect)
        # Color name
        ax1.text(i + 0.5, 0.5, name.replace('_', '\n'), ha='center', va='center', 
                fontsize=8, fontweight='bold')
        # Hex code
        ax1.text(i + 0.5, -0.2, color, ha='center', va='top', fontsize=7)
    
    ax1.set_xlim(0, n_colors)
    ax1.set_ylim(-0.3, 1.2)
    ax1.axis('off')
    
    # Cognitive scale gradient
    ax2.set_title('Cognitive Scale Gradient', fontsize=14, fontweight='bold')
    gradient = COLOR_GRADIENTS['cognitive_scale']
    
    for i, color in enumerate(gradient):
        rect = mpatches.Rectangle((i, 0), 1, 1, facecolor=color, edgecolor='black', linewidth=1)
        ax2.add_patch(rect)
        ax2.text(i + 0.5, 0.5, f'Level {i+1}', ha='center', va='center', fontsize=9)
        ax2.text(i + 0.5, -0.2, color, ha='center', va='top', fontsize=7)
    
    ax2.set_xlim(0, len(gradient))
    ax2.set_ylim(-0.3, 1.2)
    ax2.axis('off')
    
    # Metric colors examples
    ax3.set_title('Metric-Specific Colors', fontsize=14, fontweight='bold')
    metric_examples = [
        ('cognitive_offloading', 'Cognitive\nOffloading'),
        ('deep_thinking', 'Deep\nThinking'),
        ('scaffolding', 'Scaffolding'),
        ('knowledge_integration', 'Knowledge\nIntegration'),
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert')
    ]
    
    for i, (key, label) in enumerate(metric_examples):
        color = METRIC_COLORS[key]
        rect = mpatches.Rectangle((i, 0), 1, 1, facecolor=color, edgecolor='black', linewidth=1)
        ax3.add_patch(rect)
        ax3.text(i + 0.5, 0.5, label, ha='center', va='center', fontsize=8, fontweight='bold')
        ax3.text(i + 0.5, -0.2, color, ha='center', va='top', fontsize=7)
    
    ax3.set_xlim(0, len(metric_examples))
    ax3.set_ylim(-0.3, 1.2)
    ax3.axis('off')
    
    plt.suptitle('MEGA Thesis Color Palette Reference', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig('thesis_color_palette_reference.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

if __name__ == "__main__":
    create_color_palette_reference()
    print("Created thesis_color_palette_reference.png")