"""
Alternative launcher for the MEGA Test Dashboard
Handles import paths correctly
"""

import subprocess
import sys
import os

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Add thesis-agents to path for MENTOR environment
thesis_agents_dir = os.path.join(current_dir, 'thesis-agents')
sys.path.insert(0, thesis_agents_dir)

def launch_test_dashboard():
    """Launch the test dashboard using streamlit"""
    print("🚀 Launching MEGA Test Dashboard...")
    print("-" * 50)
    print("Test Groups:")
    print("1. MENTOR - Multi-agent scaffolding")
    print("2. Generic AI - Direct assistance")
    print("3. Control - No AI assistance")
    print("-" * 50)
    
    # Set environment variable to handle imports
    os.environ['PYTHONPATH'] = f"{current_dir}{os.pathsep}{thesis_agents_dir}"
    
    # Path to test dashboard
    dashboard_path = os.path.join("thesis_tests", "test_dashboard.py")
    
    # Launch with streamlit
    try:
        # Use the current Python interpreter
        cmd = [sys.executable, "-m", "streamlit", "run", dashboard_path]
        
        # Set the environment for the subprocess
        env = os.environ.copy()
        env['PYTHONPATH'] = f"{current_dir}{os.pathsep}{thesis_agents_dir}"
        
        subprocess.run(cmd, env=env)
    except KeyboardInterrupt:
        print("\n\n✅ Test Dashboard closed.")
    except Exception as e:
        print(f"\n❌ Error launching dashboard: {e}")
        print("\nPlease ensure you have installed the requirements:")
        print("pip install -r thesis_tests/requirements_tests.txt")

if __name__ == "__main__":
    launch_test_dashboard()