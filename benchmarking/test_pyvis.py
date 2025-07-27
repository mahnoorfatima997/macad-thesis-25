"""
Quick test script to verify PyVis visualizations are working
"""

from graph_ml_pyvis import PyVisGraphMLVisualizer

# Initialize visualizer
print("Initializing PyVis visualizer...")
viz = PyVisGraphMLVisualizer()

# Test individual visualizations
print("\nTesting individual visualizations:")

print("1. Knowledge Graph...", end='')
try:
    viz.create_knowledge_graph("test_knowledge.html")
    print(" OK")
except Exception as e:
    print(f" Error: {e}")

print("2. Learning Trajectories...", end='')
try:
    viz.create_learning_trajectory_network("test_trajectories.html")
    print(" OK")
except Exception as e:
    print(f" Error: {e}")

print("3. Agent Collaboration...", end='')
try:
    viz.create_agent_collaboration_network("test_agents.html")
    print(" OK")
except Exception as e:
    print(f" Error: {e}")

print("4. Cognitive Patterns...", end='')
try:
    viz.create_cognitive_pattern_network("test_cognitive.html")
    print(" OK")
except Exception as e:
    print(f" Error: {e}")

print("5. Session Evolution...", end='')
try:
    viz.create_session_evolution_network("test_evolution.html")
    print(" OK")
except Exception as e:
    print(f" Error: {e}")

print("\nAll tests completed!")
print("Check the benchmarking/results/visualizations/ directory for test files.")