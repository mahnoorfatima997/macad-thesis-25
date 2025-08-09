"""
Entry point for the Unified Architectural Dashboard.
Ensures correct import paths and environment loading when launched directly.
"""

import os
import sys

# Project root
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Ensure project root is on sys.path
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Ensure thesis-agents package is importable as a top-level package
THESIS_AGENTS_DIR = os.path.join(PROJECT_ROOT, 'thesis-agents')
if THESIS_AGENTS_DIR not in sys.path:
    sys.path.insert(0, THESIS_AGENTS_DIR)

# Load environment variables from .env at project root if present
try:
    from dotenv import load_dotenv
    env_path = os.path.join(PROJECT_ROOT, '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path, override=True)
    else:
        load_dotenv()
except Exception:
    pass

from dashboard import UnifiedArchitecturalDashboard

def main():
    """Main function to run the dashboard."""
    dashboard = UnifiedArchitecturalDashboard()
    dashboard.run()

if __name__ == "__main__":
    main() 