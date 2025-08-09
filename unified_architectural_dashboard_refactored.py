"""
Entry point for the refactored Unified Architectural Dashboard.

This file serves as the main entry point and imports the refactored dashboard.
"""

import sys
import os

# Add the current directory to the path so we can import the dashboard package
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dashboard import UnifiedArchitecturalDashboard

def main():
    """Main function to run the refactored dashboard."""
    dashboard = UnifiedArchitecturalDashboard()
    dashboard.run()

if __name__ == "__main__":
    main() 