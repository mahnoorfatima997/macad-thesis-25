#!/usr/bin/env python
"""
Launch the Cognitive Benchmarking Dashboard
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Launch the Streamlit dashboard"""
    
    print("="*60)
    print("MEGA ARCHITECTURAL MENTOR - BENCHMARKING DASHBOARD")
    print("="*60)
    print("\nLaunching dashboard...")
    print("Please wait for your browser to open...")
    print("\nPress Ctrl+C to stop the dashboard\n")
    
    # Get the path to the dashboard script
    dashboard_path = Path(__file__).parent / "benchmark_dashboard.py"
    
    # Launch Streamlit
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run",
            str(dashboard_path),
            "--theme.base", "light",
            "--theme.primaryColor", "#1f77b4",
            "--theme.backgroundColor", "#ffffff",
            "--theme.secondaryBackgroundColor", "#f0f2f6",
            "--theme.textColor", "#262730"
        ])
    except KeyboardInterrupt:
        print("\n\nDashboard stopped.")
    except Exception as e:
        print(f"\nError launching dashboard: {str(e)}")
        print("\nMake sure Streamlit is installed: pip install streamlit")

if __name__ == "__main__":
    main()