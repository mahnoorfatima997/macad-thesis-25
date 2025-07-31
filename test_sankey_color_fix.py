"""
Test that the Sankey color format fix works correctly
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'benchmarking'))

from linkography_visualization import LinkographVisualizer

def test_sankey_color_conversion():
    """Test Sankey color conversion"""
    print("Testing Sankey diagram color conversion...")
    print("=" * 60)
    
    visualizer = LinkographVisualizer()
    
    # Test the conversion for different phase colors
    test_cases = [
        ('ideation', '#cd766d'),      # accent_coral
        ('visualization', '#d99c66'),  # neutral_orange  
        ('materialization', '#784c80') # primary_violet
    ]
    
    print("Phase color conversions for Sankey links:")
    for phase, expected_color in test_cases:
        phase_color = visualizer._get_phase_color(phase)
        rgba_color = visualizer._hex_to_rgba(phase_color, 0.25)
        print(f"  {phase}: {phase_color} -> {rgba_color}")
        
        # Verify it starts with rgba
        assert rgba_color.startswith('rgba('), f"Color should start with 'rgba(' but got {rgba_color}"
        assert rgba_color.endswith(')'), f"Color should end with ')' but got {rgba_color}"
    
    print("\n[SUCCESS] Sankey color conversion working correctly!")
    print("The Linkography Analysis tab should now display Sankey diagrams without errors.")

if __name__ == "__main__":
    test_sankey_color_conversion()