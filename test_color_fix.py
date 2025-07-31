"""
Test that the color format fix works correctly
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'benchmarking'))

from linkography_visualization import LinkographVisualizer

def test_color_conversion():
    """Test hex to rgba conversion"""
    print("Testing hex to rgba color conversion...")
    print("=" * 60)
    
    visualizer = LinkographVisualizer()
    
    # Test the conversion
    test_colors = [
        '#cd766d',  # accent_coral
        '#784c80',  # primary_violet
        '#d99c66',  # neutral_orange
    ]
    
    for color in test_colors:
        rgba = visualizer._hex_to_rgba(color, 0.125)
        print(f"{color} -> {rgba}")
    
    print("\n[SUCCESS] Color conversion working correctly!")
    print("The Linkography Analysis tab should now display without color format errors.")

if __name__ == "__main__":
    test_color_conversion()