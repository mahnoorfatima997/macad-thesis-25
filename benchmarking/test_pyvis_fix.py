"""Test PyVis visualization fix"""

from pyvis.network import Network
import os

# Create output directory
os.makedirs("benchmarking/results/visualizations/pyvis", exist_ok=True)

# Create a simple network with the fixed approach
net = Network(
    height="800px", 
    width="100%", 
    bgcolor="#ffffff",
    font_color="#4f3a3e",
    notebook=False,
    cdn_resources='in_line',  # This is crucial - includes all JS inline
    select_menu=False,
    filter_menu=False
)

# Add some test nodes
net.add_node(1, label="Test Node 1", color="#5c4f73", size=30)
net.add_node(2, label="Test Node 2", color="#784c80", size=30)
net.add_node(3, label="Test Node 3", color="#b87189", size=30)

# Add edges
net.add_edge(1, 2, color="#e0ceb5")
net.add_edge(2, 3, color="#e0ceb5")
net.add_edge(3, 1, color="#e0ceb5")

# Configure physics
net.barnes_hut(gravity=-5000, central_gravity=0.3, spring_length=100)

# Use save_graph() with manual HTML generation to avoid encoding issues
output_file = "benchmarking/results/visualizations/pyvis/test_fixed.html"

# Generate the HTML manually to control encoding
html = net.generate_html(notebook=False)

# Write with UTF-8 encoding
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"Test graph saved to: {output_file}")
print("Open this file in a browser to verify the graph displays correctly.")