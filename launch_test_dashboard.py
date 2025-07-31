"""
Quick launcher for the MEGA Test Dashboard
"""

import subprocess
import sys
import os

def launch_test_dashboard():
    """Launch the test dashboard using streamlit"""
    print("🚀 Launching MEGA Test Dashboard...")
    print("-" * 50)
    print("Test Groups:")
    print("1. MENTOR - Multi-agent scaffolding")
    print("2. Generic AI - Direct assistance")
    print("3. Control - No AI assistance")
    print("-" * 50)
    
    # Path to test dashboard
    dashboard_path = os.path.join("thesis_tests", "test_dashboard.py")
    
    # Launch with streamlit
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", dashboard_path])
    except KeyboardInterrupt:
        print("\n\n✅ Test Dashboard closed.")
    except Exception as e:
        print(f"\n❌ Error launching dashboard: {e}")
        print("\nPlease ensure you have installed the requirements:")
        print("pip install -r thesis_tests/requirements_tests.txt")

if __name__ == "__main__":
    launch_test_dashboard()