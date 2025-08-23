"""
Entry point for the Unified Architectural Dashboard.
Ensures correct import paths and environment loading when launched directly.
"""

# Fix for SQLite version issue on Streamlit Cloud
# This must be done before any other imports that might use SQLite
try:
    import pysqlite3
    import sys
    sys.modules['sqlite3'] = pysqlite3
    print("✅ Using pysqlite3 for ChromaDB compatibility")
except ImportError:
    # pysqlite3-binary not available, use system sqlite3
    # Patch SQLite version check for ChromaDB compatibility
    import sqlite3
    print(f"ℹ️ Using system SQLite version: {sqlite3.sqlite_version}")

    # Check if version is sufficient (3.35.0 required, we have 3.38.4)
    version_parts = [int(x) for x in sqlite3.sqlite_version.split('.')]
    if version_parts[0] > 3 or (version_parts[0] == 3 and version_parts[1] >= 35):
        print("✅ SQLite version is sufficient for ChromaDB")
        # Monkey patch to bypass ChromaDB's version check
        import sys

        # Create a mock pysqlite3 module that uses system sqlite3
        class MockPySQLite3:
            def __getattr__(self, name):
                return getattr(sqlite3, name)

        sys.modules['pysqlite3'] = MockPySQLite3()
        sys.modules['pysqlite3.dbapi2'] = sqlite3
        print("✅ Created SQLite compatibility layer for ChromaDB")
    else:
        print(f"⚠️ SQLite version {sqlite3.sqlite_version} may be too old for ChromaDB")

import os
import sys

# Set environment variables to prevent GUI dependencies before any imports
os.environ['OPENCV_IO_ENABLE_OPENEXR'] = '0'
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
os.environ['MPLBACKEND'] = 'Agg'

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