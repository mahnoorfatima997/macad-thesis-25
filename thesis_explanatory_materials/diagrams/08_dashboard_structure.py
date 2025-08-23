"""
Dashboard Structure Overview Diagram Generator
Creates visual representation of the dashboard sections and components
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Rectangle, Polygon
import numpy as np
import os
import sys

# Add the benchmarking directory to the path to import thesis colors
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'benchmarking'))
from thesis_colors import THESIS_COLORS, METRIC_COLORS, UI_COLORS

def create_dashboard_structure_diagram():
    """Create comprehensive dashboard structure overview"""
    
    # Create figure with proper sizing
    fig, ax = plt.subplots(1, 1, figsize=(20, 14))
    
    # Define dashboard components with hierarchical structure
    components = {
        # Header Section
        'header': {
            'pos': (10, 12.5), 'size': (18, 1),
            'color': THESIS_COLORS['primary_dark'],
            'text': 'MEGA Architectural Mentor Dashboard',
            'type': 'header'
        },
        
        # Navigation Menu
        'nav_menu': {
            'pos': (2, 11), 'size': (3, 0.8),
            'color': THESIS_COLORS['primary_purple'],
            'text': 'Navigation\nMenu',
            'type': 'navigation'
        },
        
        # Main Dashboard Sections
        'chat_interface': {
            'pos': (7, 11), 'size': (5, 1.5),
            'color': THESIS_COLORS['primary_violet'],
            'text': 'Interactive Chat Interface',
            'type': 'main_section',
            'subsections': [
                'Message History', 'Input Field', 'Agent Status', 'Response Area'
            ]
        },
        
        'session_overview': {
            'pos': (14, 11), 'size': (5, 1.5),
            'color': THESIS_COLORS['primary_rose'],
            'text': 'Session Overview',
            'type': 'main_section',
            'subsections': [
                'Current Session', 'Progress Tracker', 'Time Analytics', 'Phase Status'
            ]
        },
        
        # Analytics Sections
        'cognitive_metrics': {
            'pos': (4, 9), 'size': (4, 1.5),
            'color': METRIC_COLORS['cognitive_offloading'],
            'text': 'Cognitive Metrics Panel',
            'type': 'analytics',
            'subsections': [
                'COP Score', 'DTE Level', 'SE Rating', 'KI Index'
            ]
        },
        
        'anthropomorphism_metrics': {
            'pos': (10, 9), 'size': (4, 1.5),
            'color': THESIS_COLORS['accent_coral'],
            'text': 'Anthropomorphism Prevention',
            'type': 'analytics',
            'subsections': [
                'CAI Score', 'ADS Level', 'NES Rating', 'PBI Index'
            ]
        },
        
        'learning_analytics': {
            'pos': (16, 9), 'size': (4, 1.5),
            'color': THESIS_COLORS['neutral_warm'],
            'text': 'Learning Analytics',
            'type': 'analytics',
            'subsections': [
                'Progression', 'Engagement', 'Metacognition', 'Performance'
            ]
        },
        
        # Visualization Sections
        'linkography_viz': {
            'pos': (3, 6.5), 'size': (4, 1.5),
            'color': THESIS_COLORS['primary_pink'],
            'text': 'Linkography Visualization',
            'type': 'visualization',
            'subsections': [
                'Design Moves', 'Link Patterns', 'Critical Moves', 'Flow Analysis'
            ]
        },
        
        'graph_ml_viz': {
            'pos': (8, 6.5), 'size': (4, 1.5),
            'color': THESIS_COLORS['accent_magenta'],
            'text': 'Graph ML Visualizations',
            'type': 'visualization',
            'subsections': [
                'Network Graph', 'Embedding Space', 'Pattern Recognition', 'Clustering'
            ]
        },
        
        'performance_charts': {
            'pos': (13, 6.5), 'size': (4, 1.5),
            'color': THESIS_COLORS['neutral_orange'],
            'text': 'Performance Charts',
            'type': 'visualization',
            'subsections': [
                'Radar Chart', 'Trend Lines', 'Comparison Bars', 'Heatmaps'
            ]
        },
        
        'interactive_reports': {
            'pos': (17, 6.5), 'size': (3, 1.5),
            'color': THESIS_COLORS['primary_violet'],
            'text': 'Interactive Reports',
            'type': 'visualization',
            'subsections': [
                'Drill-down', 'Export Options', 'Filters', 'Customization'
            ]
        },
        
        # Data Management Sections
        'session_management': {
            'pos': (4, 4), 'size': (4, 1.2),
            'color': THESIS_COLORS['neutral_light'],
            'text': 'Session Management',
            'type': 'data_management',
            'subsections': [
                'Session List', 'Create New', 'Import/Export', 'Archive'
            ]
        },
        
        'data_export': {
            'pos': (10, 4), 'size': (4, 1.2),
            'color': THESIS_COLORS['primary_dark'],
            'text': 'Data Export Hub',
            'type': 'data_management',
            'subsections': [
                'CSV Export', 'JSON Export', 'PDF Reports', 'Dropbox Sync'
            ]
        },
        
        'settings_config': {
            'pos': (16, 4), 'size': (4, 1.2),
            'color': THESIS_COLORS['primary_purple'],
            'text': 'Settings & Configuration',
            'type': 'data_management',
            'subsections': [
                'User Preferences', 'Metric Thresholds', 'Display Options', 'API Config'
            ]
        },
        
        # Footer Section
        'status_bar': {
            'pos': (10, 1.5), 'size': (18, 0.6),
            'color': THESIS_COLORS['neutral_warm'],
            'text': 'Status Bar: System Health • Data Status • Export Progress • Notifications',
            'type': 'footer'
        }
    }
    
    # Draw components
    for comp_name, comp in components.items():
        x, y = comp['pos']
        width, height = comp['size']
        color = comp['color']
        comp_type = comp['type']
        
        # Different styling for different component types
        if comp_type == 'header':
            box = FancyBboxPatch(
                (x - width/2, y - height/2), width, height,
                boxstyle="round,pad=0.1",
                facecolor=color, edgecolor='white', linewidth=3, alpha=0.9
            )
            text_color = 'white'
            font_size = 16
            font_weight = 'bold'
            
        elif comp_type == 'navigation':
            box = FancyBboxPatch(
                (x - width/2, y - height/2), width, height,
                boxstyle="round,pad=0.05",
                facecolor=color, edgecolor='white', linewidth=2, alpha=0.8
            )
            text_color = 'white'
            font_size = 10
            font_weight = 'bold'
            
        elif comp_type == 'main_section':
            box = FancyBboxPatch(
                (x - width/2, y - height/2), width, height,
                boxstyle="round,pad=0.1",
                facecolor=color, edgecolor='white', linewidth=3, alpha=0.85
            )
            text_color = 'white'
            font_size = 12
            font_weight = 'bold'
            
        elif comp_type == 'analytics':
            box = FancyBboxPatch(
                (x - width/2, y - height/2), width, height,
                boxstyle="sawtooth,pad=0.05",
                facecolor=color, edgecolor='white', linewidth=2, alpha=0.8
            )
            text_color = 'white'
            font_size = 11
            font_weight = 'bold'
            
        elif comp_type == 'visualization':
            # Hexagonal style for visualizations
            angles = np.linspace(0, 2*np.pi, 7)
            hex_width = width * 0.4
            hex_height = height * 0.4
            hex_points = [(x + hex_width * np.cos(a), y + hex_height * np.sin(a)) for a in angles[:-1]]
            box = Polygon(hex_points, facecolor=color, edgecolor='white', linewidth=2, alpha=0.8)
            text_color = 'white'
            font_size = 10
            font_weight = 'bold'
            
        elif comp_type == 'data_management':
            box = FancyBboxPatch(
                (x - width/2, y - height/2), width, height,
                boxstyle="round,pad=0.08",
                facecolor=color, edgecolor='white', linewidth=2, alpha=0.75
            )
            text_color = 'white'
            font_size = 10
            font_weight = 'bold'
            
        else:  # footer
            box = Rectangle(
                (x - width/2, y - height/2), width, height,
                facecolor=color, edgecolor='white', linewidth=1, alpha=0.7
            )
            text_color = THESIS_COLORS['primary_dark']
            font_size = 9
            font_weight = 'normal'
        
        ax.add_patch(box)
        
        # Add main text
        ax.text(x, y + 0.1, comp['text'], ha='center', va='center',
               fontsize=font_size, fontweight=font_weight, color=text_color)
        
        # Add subsections if available
        if 'subsections' in comp and comp_type != 'footer':
            subsections_text = ' • '.join(comp['subsections'])
            ax.text(x, y - 0.4, subsections_text, ha='center', va='center',
                   fontsize=8, color=text_color, style='italic', alpha=0.9)
    
    # Define component relationships and data flow
    data_flows = [
        # From chat interface to analytics
        ('chat_interface', 'cognitive_metrics'),
        ('chat_interface', 'anthropomorphism_metrics'),
        ('chat_interface', 'learning_analytics'),
        
        # From analytics to visualizations
        ('cognitive_metrics', 'linkography_viz'),
        ('anthropomorphism_metrics', 'graph_ml_viz'),
        ('learning_analytics', 'performance_charts'),
        
        # From visualizations to reports
        ('linkography_viz', 'interactive_reports'),
        ('graph_ml_viz', 'interactive_reports'),
        ('performance_charts', 'interactive_reports'),
        
        # To data management
        ('session_overview', 'session_management'),
        ('interactive_reports', 'data_export'),
        
        # Navigation connections
        ('nav_menu', 'chat_interface'),
        ('nav_menu', 'session_overview'),
    ]
    
    # Draw data flow arrows
    for source, target in data_flows:
        source_pos = components[source]['pos']
        target_pos = components[target]['pos']
        
        arrow = FancyArrowPatch(
            source_pos, target_pos,
            arrowstyle='->', mutation_scale=12,
            color=THESIS_COLORS['primary_dark'], linewidth=1.5, alpha=0.4,
            connectionstyle="arc3,rad=0.1"
        )
        ax.add_patch(arrow)
    
    # Add section labels
    section_labels = [
        {'pos': (10, 12), 'text': 'HEADER & NAVIGATION', 'color': THESIS_COLORS['primary_dark']},
        {'pos': (10, 10.3), 'text': 'MAIN INTERACTION PANELS', 'color': THESIS_COLORS['primary_violet']},
        {'pos': (10, 8.3), 'text': 'REAL-TIME ANALYTICS', 'color': THESIS_COLORS['accent_coral']},
        {'pos': (10, 5.8), 'text': 'INTERACTIVE VISUALIZATIONS', 'color': THESIS_COLORS['primary_pink']},
        {'pos': (10, 3.3), 'text': 'DATA MANAGEMENT & EXPORT', 'color': THESIS_COLORS['neutral_light']},
        {'pos': (10, 0.8), 'text': 'STATUS & NOTIFICATIONS', 'color': THESIS_COLORS['neutral_warm']},
    ]
    
    for label in section_labels:
        ax.text(label['pos'][0], label['pos'][1], label['text'],
               ha='center', va='center', fontsize=13, fontweight='bold',
               color=label['color'], style='italic',
               bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.9))
    
    # Add user interaction flow indicators
    user_flows = [
        {'pos': (1, 9), 'text': 'User\nInteraction', 'target': (7, 11)},
        {'pos': (1, 6.5), 'text': 'Analysis\nReview', 'target': (10, 9)},
        {'pos': (1, 4), 'text': 'Data\nExport', 'target': (10, 4)},
    ]
    
    for flow in user_flows:
        # User icon (simplified)
        user_circle = Circle(flow['pos'], 0.3, facecolor=THESIS_COLORS['accent_magenta'],
                           edgecolor='white', linewidth=2, alpha=0.8)
        ax.add_patch(user_circle)
        ax.text(flow['pos'][0], flow['pos'][1], '👤', ha='center', va='center', fontsize=12)
        
        # Flow text
        ax.text(flow['pos'][0], flow['pos'][1] - 0.6, flow['text'],
               ha='center', va='center', fontsize=9, fontweight='bold',
               color=THESIS_COLORS['accent_magenta'])
        
        # Flow arrow to target
        arrow = FancyArrowPatch(
            flow['pos'], flow['target'],
            arrowstyle='->', mutation_scale=15,
            color=THESIS_COLORS['accent_magenta'], linewidth=2, alpha=0.6,
            connectionstyle="arc3,rad=0.2"
        )
        ax.add_patch(arrow)
    
    # Add technology stack indicators
    tech_indicators = [
        {'pos': (19, 11), 'text': 'Streamlit\nFramework', 'color': THESIS_COLORS['primary_purple']},
        {'pos': (19, 9), 'text': 'Plotly\nVisualizations', 'color': THESIS_COLORS['accent_magenta']},
        {'pos': (19, 6.5), 'text': 'NetworkX\nGraphs', 'color': THESIS_COLORS['primary_pink']},
        {'pos': (19, 4), 'text': 'Pandas\nData Processing', 'color': THESIS_COLORS['neutral_orange']},
    ]
    
    for tech in tech_indicators:
        tech_box = FancyBboxPatch(
            (tech['pos'][0] - 0.8, tech['pos'][1] - 0.3), 1.6, 0.6,
            boxstyle="round,pad=0.05",
            facecolor=THESIS_COLORS['neutral_light'], 
            edgecolor=tech['color'], linewidth=1.5, alpha=0.8
        )
        ax.add_patch(tech_box)
        
        ax.text(tech['pos'][0], tech['pos'][1], tech['text'],
               ha='center', va='center', fontsize=8, fontweight='bold',
               color=tech['color'])
    
    # Add responsive design indicators
    responsive_sizes = [
        {'pos': (0.5, 12), 'size': 0.3, 'label': 'Desktop'},
        {'pos': (0.5, 11.5), 'size': 0.2, 'label': 'Tablet'},
        {'pos': (0.5, 11), 'size': 0.15, 'label': 'Mobile'},
    ]
    
    for device in responsive_sizes:
        device_rect = Rectangle(
            (device['pos'][0] - device['size']/2, device['pos'][1] - 0.1), 
            device['size'], 0.2,
            facecolor=THESIS_COLORS['primary_violet'], 
            edgecolor='white', linewidth=1, alpha=0.7
        )
        ax.add_patch(device_rect)
        
        ax.text(device['pos'][0] + 0.3, device['pos'][1], device['label'],
               ha='left', va='center', fontsize=8, 
               color=THESIS_COLORS['primary_violet'])
    
    # Set axis properties
    ax.set_xlim(-1, 21)
    ax.set_ylim(0.5, 13.5)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Add title
    ax.text(10, 13.2, 'MEGA Architectural Mentor - Dashboard Architecture',
           fontsize=18, fontweight='bold', ha='center',
           color=THESIS_COLORS['primary_dark'])
    
    # Add subtitle
    ax.text(10, 12.9, 'Comprehensive Educational AI Interface Structure',
           fontsize=12, ha='center', style='italic',
           color=THESIS_COLORS['primary_purple'])
    
    # Create legend
    legend_elements = [
        mpatches.Patch(color=THESIS_COLORS['primary_violet'], label='Core Interface'),
        mpatches.Patch(color=THESIS_COLORS['accent_coral'], label='Analytics'),
        mpatches.Patch(color=THESIS_COLORS['primary_pink'], label='Visualizations'),
        mpatches.Patch(color=THESIS_COLORS['neutral_light'], label='Data Management'),
        mpatches.Patch(color=THESIS_COLORS['accent_magenta'], label='User Interactions'),
    ]
    
    ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(0.02, 0.98),
             frameon=True, fancybox=True, shadow=True)
    
    plt.tight_layout()
    return fig

def save_diagram():
    """Save the diagram in multiple formats"""
    fig = create_dashboard_structure_diagram()
    
    # Define output paths
    base_path = os.path.dirname(__file__)
    png_path = os.path.join(base_path, '08_dashboard_structure.png')
    svg_path = os.path.join(base_path, '08_dashboard_structure.svg')
    
    # Save as PNG with high DPI
    fig.savefig(png_path, dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    
    # Save as SVG for scalability
    fig.savefig(svg_path, format='svg', bbox_inches='tight',
                facecolor='white', edgecolor='none')
    
    print(f"Dashboard Structure diagram saved:")
    print(f"  PNG: {png_path}")
    print(f"  SVG: {svg_path}")
    
    plt.close(fig)

if __name__ == "__main__":
    save_diagram()