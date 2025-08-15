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

# Initialize secrets manager for API keys and configuration
# This will handle both Streamlit secrets and environment variables
try:
    sys.path.insert(0, os.path.join(PROJECT_ROOT, 'thesis-agents'))
    from utils.secrets_manager import secrets_manager
    # Test that secrets are available
    api_key = secrets_manager.get_secret('OPENAI_API_KEY')
    if api_key:
        print("✅ Secrets manager initialized successfully")
    else:
        print("⚠️ Warning: OPENAI_API_KEY not found in secrets or environment")
except ImportError as e:
    print(f"⚠️ Warning: Could not import secrets manager: {e}")
    # Fallback to dotenv for local development
    try:
        from dotenv import load_dotenv
        env_path = os.path.join(PROJECT_ROOT, '.env')
        if os.path.exists(env_path):
            load_dotenv(env_path, override=True)
        else:
            load_dotenv()
        print("✅ Fallback to dotenv successful")
    except Exception as fallback_e:
        print(f"⚠️ Warning: Could not load environment variables: {fallback_e}")
except Exception as e:
    print(f"⚠️ Warning: Secrets manager initialization failed: {e}")

from dashboard.unified_dashboard import UnifiedArchitecturalDashboard

def main():
    """Main function to run the dashboard."""
    dashboard = UnifiedArchitecturalDashboard()
    dashboard.run()

if __name__ == "__main__":
    main() 