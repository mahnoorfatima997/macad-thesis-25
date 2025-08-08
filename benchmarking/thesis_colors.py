"""
MEGA Architectural Mentor - Custom Thesis Color Palette
Centralized color configuration for all visualizations
"""

# Primary thesis colors from the custom palette
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

# Semantic color mappings for different metric types
METRIC_COLORS = {
    # Cognitive metrics
    'cognitive_offloading': THESIS_COLORS['primary_purple'],
    'deep_thinking': THESIS_COLORS['primary_violet'],
    'scaffolding': THESIS_COLORS['primary_dark'],  # Dark burgundy - distinct from rose
    'knowledge_integration': THESIS_COLORS['neutral_warm'],
    'engagement': THESIS_COLORS['neutral_orange'],
    'metacognition': THESIS_COLORS['accent_coral'],
    
    # Proficiency levels
    'beginner': THESIS_COLORS['accent_coral'],
    'intermediate': THESIS_COLORS['neutral_orange'],
    'advanced': THESIS_COLORS['primary_violet'],
    'expert': THESIS_COLORS['primary_dark'],
    
    # Agent types
    'socratic_tutor': THESIS_COLORS['primary_purple'],
    'domain_expert': THESIS_COLORS['primary_violet'],
    'cognitive_enhancement': THESIS_COLORS['primary_rose'],
    'analysis_agent': THESIS_COLORS['neutral_warm'],
    'context_agent': THESIS_COLORS['neutral_light'],
    
    # Performance indicators
    'excellent': THESIS_COLORS['primary_dark'],
    'good': THESIS_COLORS['primary_purple'],
    'moderate': THESIS_COLORS['neutral_orange'],
    'needs_improvement': THESIS_COLORS['accent_coral'],
}

# Color gradients for continuous scales
COLOR_GRADIENTS = {
    'performance': [
        THESIS_COLORS['accent_coral'],      # Low
        THESIS_COLORS['neutral_orange'],    # Medium-low
        THESIS_COLORS['neutral_warm'],      # Medium
        THESIS_COLORS['primary_violet'],    # Medium-high
        THESIS_COLORS['primary_dark']       # High
    ],
    
    'cognitive_scale': [
        '#cd766d',  # Lowest
        '#d99c66',
        '#dcc188',
        '#cda29a',
        '#b87189',
        '#784c80',
        '#5c4f73',
        '#4f3a3e'   # Highest
    ],
    
    'heatmap': [
        THESIS_COLORS['accent_coral'],      # Cold/Low
        THESIS_COLORS['neutral_orange'],
        THESIS_COLORS['neutral_warm'],
        THESIS_COLORS['primary_pink'],
        THESIS_COLORS['primary_violet']     # Hot/High
    ]
}

# Plotly color scales
PLOTLY_COLORSCALES = {
    'main': [
        [0.0, THESIS_COLORS['accent_coral']],
        [0.25, THESIS_COLORS['neutral_orange']],
        [0.5, THESIS_COLORS['neutral_warm']],
        [0.75, THESIS_COLORS['primary_violet']],
        [1.0, THESIS_COLORS['primary_dark']]
    ],
    
    'diverging': [
        [0.0, THESIS_COLORS['accent_coral']],      # Strong negative correlation (red-ish)
        [0.25, THESIS_COLORS['primary_pink']],      # Weak negative 
        [0.5, THESIS_COLORS['neutral_light']],      # No correlation (neutral)
        [0.75, THESIS_COLORS['primary_violet']],    # Weak positive
        [1.0, THESIS_COLORS['primary_dark']]        # Strong positive correlation (dark)
    ],
    
    'sequential': [
        [0.0, THESIS_COLORS['neutral_light']],
        [0.33, THESIS_COLORS['primary_pink']],
        [0.66, THESIS_COLORS['primary_violet']],
        [1.0, THESIS_COLORS['primary_dark']]
    ]
}

# Chart-specific color schemes
CHART_COLORS = {
    'bar_chart': [
        THESIS_COLORS['primary_purple'],
        THESIS_COLORS['primary_violet'],
        THESIS_COLORS['primary_rose'],
        THESIS_COLORS['neutral_warm'],
        THESIS_COLORS['neutral_orange']
    ],
    
    'pie_chart': [
        THESIS_COLORS['primary_dark'],
        THESIS_COLORS['primary_purple'],
        THESIS_COLORS['primary_violet'],
        THESIS_COLORS['primary_rose'],
        THESIS_COLORS['neutral_warm'],
        THESIS_COLORS['neutral_orange']
    ],
    
    'line_chart': [
        THESIS_COLORS['primary_purple'],
        THESIS_COLORS['accent_coral'],
        THESIS_COLORS['primary_violet'],
        THESIS_COLORS['neutral_warm']
    ],
    
    'scatter': [
        THESIS_COLORS['primary_violet'],
        THESIS_COLORS['accent_coral'],
        THESIS_COLORS['neutral_orange'],
        THESIS_COLORS['primary_purple']
    ]
}

# Background and text colors
UI_COLORS = {
    'background': '#faf8f5',
    'surface': '#ffffff',
    'text_primary': '#2c2328',
    'text_secondary': '#5c4f73',
    'border': '#e0ceb5',
    'shadow': 'rgba(79, 58, 62, 0.1)'
}

def get_color_palette(chart_type='default', n_colors=None):
    """
    Get appropriate color palette for a specific chart type
    
    Args:
        chart_type: Type of chart ('bar', 'pie', 'line', 'scatter', etc.)
        n_colors: Number of colors needed (will cycle if more needed)
    
    Returns:
        List of color hex codes
    """
    if chart_type in ['bar', 'bar_chart']:
        colors = CHART_COLORS['bar_chart']
    elif chart_type in ['pie', 'pie_chart']:
        colors = CHART_COLORS['pie_chart']
    elif chart_type in ['line', 'line_chart']:
        colors = CHART_COLORS['line_chart']
    elif chart_type in ['scatter', 'scatter_plot']:
        colors = CHART_COLORS['scatter']
    else:
        colors = list(THESIS_COLORS.values())
    
    if n_colors and n_colors > len(colors):
        # Cycle colors if more needed
        colors = colors * (n_colors // len(colors) + 1)
    
    return colors[:n_colors] if n_colors else colors

def get_metric_color(metric_name):
    """Get color for a specific metric"""
    metric_lower = metric_name.lower().replace(' ', '_')
    
    # Check exact matches
    if metric_lower in METRIC_COLORS:
        return METRIC_COLORS[metric_lower]
    
    # Check partial matches
    for key, color in METRIC_COLORS.items():
        if key in metric_lower or metric_lower in key:
            return color
    
    # Default to primary purple
    return THESIS_COLORS['primary_purple']

def get_proficiency_color(proficiency_level):
    """Get color for proficiency level"""
    return METRIC_COLORS.get(proficiency_level.lower(), THESIS_COLORS['neutral_warm'])

def get_agent_color(agent_name):
    """Get color for agent type"""
    agent_lower = agent_name.lower().replace(' ', '_')
    
    for key, color in METRIC_COLORS.items():
        if key in agent_lower or agent_lower in key:
            return color
    
    return THESIS_COLORS['neutral_warm']