"""
Launcher for the full test dashboard (all three groups)
Supports MENTOR, Generic AI, and Control groups
"""

import subprocess
import sys
import os

def launch_full_test():
    """Launch the full test dashboard"""
    print("Launching MEGA Cognitive Benchmarking Test Dashboard")
    print("=" * 60)
    print("This dashboard supports all three test conditions:")
    print()
    print("1. MENTOR - Multi-agent scaffolding (prevents cognitive offloading)")
    print("2. Generic AI - Direct AI assistance (enables cognitive offloading)")
    print("3. Control - No AI assistance (baseline comparison)")
    print()
    print("The system will analyze design thinking patterns using Linkography")
    print("to compare cognitive development across all three conditions.")
    print("=" * 60)
    
    # Check for dependencies
    try:
        import langgraph
        print("✓ Multi-agent dependencies detected - MENTOR group available")
    except ImportError:
        print("⚠ Multi-agent dependencies not found - MENTOR group unavailable")
        print("  To enable MENTOR: pip install langgraph langchain langchain-openai")
    
    print()
    
    # Path to full test dashboard
    dashboard_path = os.path.join("thesis_tests", "test_dashboard_full.py")
    
    # Launch with streamlit
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", dashboard_path])
    except KeyboardInterrupt:
        print("\n\nTest Dashboard closed.")
    except Exception as e:
        print(f"\nError launching dashboard: {e}")
        print("\nPlease ensure you have installed the requirements:")
        print("pip install -r thesis_tests/requirements_tests.txt")

if __name__ == "__main__":
    launch_full_test()