"""Test simple PyVis graph to debug display issue"""

from pyvis.network import Network

# Create a simple test network
net = Network(height="100vh", width="100%", bgcolor="#ffffff", font_color="#4f3a3e")

# Add a few test nodes
net.add_node(1, label="Node 1", size=30, color="#5c4f73")
net.add_node(2, label="Node 2", size=30, color="#784c80")
net.add_node(3, label="Node 3", size=30, color="#b87189")

# Add edges
net.add_edge(1, 2)
net.add_edge(2, 3)
net.add_edge(3, 1)

# Configure physics
net.barnes_hut(gravity=-3000, central_gravity=0.3, spring_length=100)

# Save
net.save_graph("benchmarking/results/visualizations/pyvis/test_simple.html")
print("Test graph saved to test_simple.html")

# Also try with show method which auto-opens browser
net.show("benchmarking/results/visualizations/pyvis/test_show.html")
print("Test with show() saved to test_show.html")