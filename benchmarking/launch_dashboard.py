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
    
    # Check if we should run benchmarking analysis first
    import argparse
    parser = argparse.ArgumentParser(description='Launch the benchmarking dashboard')
    parser.add_argument('--skip-analysis', action='store_true', 
                        help='Skip running benchmarking analysis before launching dashboard')
    args = parser.parse_args()
    
    if not args.skip_analysis:
        print("\nRunning benchmarking analysis to ensure up-to-date data...")
        print("(Use --skip-analysis to skip this step)\n")
        
        # Run the benchmarking analysis
        try:
            result = subprocess.run([
                sys.executable, 
                str(Path(__file__).parent / "run_benchmarking.py"),
                "--no-dashboard"  # Don't launch dashboard from run_benchmarking
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("Benchmarking analysis completed successfully!")
            else:
                print(f"Warning: Benchmarking analysis returned error code {result.returncode}")
                if result.stderr:
                    print(f"Error: {result.stderr}")
        except Exception as e:
            print(f"Warning: Could not run benchmarking analysis: {e}")
            print("Continuing with existing data...\n")
    
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