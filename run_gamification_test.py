#!/usr/bin/env python3
"""
Simple runner script for the gamification visual test.
"""

import subprocess
import sys
import os

def main():
    """Run the gamification visual test."""
    print("🎮 LAUNCHING GAMIFICATION VISUAL TEST")
    print("=" * 60)
    
    # Check if streamlit is available
    try:
        import streamlit
        print(f"✅ Streamlit found: {streamlit.__version__}")
    except ImportError:
        print("❌ Streamlit not found. Please install with: pip install streamlit")
        return
    
    # Check if the test file exists
    test_file = "gamification_visual_test.py"
    if not os.path.exists(test_file):
        print(f"❌ Test file not found: {test_file}")
        return
    
    print(f"✅ Test file found: {test_file}")
    print()
    print("🚀 Starting Streamlit app...")
    print("📱 The app will open in your browser automatically")
    print("🔧 Use Ctrl+C to stop the server")
    print()
    
    # Launch streamlit
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", test_file,
            "--server.headless", "false",
            "--server.runOnSave", "true",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Test server stopped by user")
    except Exception as e:
        print(f"❌ Error running test: {e}")

if __name__ == "__main__":
    main()
