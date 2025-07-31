"""
Launcher for the minimal test dashboard (without MENTOR group)
Works with Generic AI and Control groups only
"""

import subprocess
import sys
import os

def launch_minimal_test():
    """Launch the minimal test dashboard"""
    print("Launching MEGA Test Dashboard (Minimal Version)...")
    print("-" * 50)
    print("Available Test Groups:")
    print("1. Generic AI - Direct AI assistance")
    print("2. Control - No AI assistance")
    print("\nNote: MENTOR group requires additional dependencies")
    print("-" * 50)
    
    # Path to minimal test dashboard
    dashboard_path = os.path.join("thesis_tests", "test_dashboard_minimal.py")
    
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
    launch_minimal_test()