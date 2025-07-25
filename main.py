#!/usr/bin/env python3
"""
Architectural AI Analysis System - Main Application
Clean, organized entry point for the architectural analysis system
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from core.unified_engine import UnifiedArchitecturalEngine

def main():
    """Main application entry point"""
    print("🏗️ Architectural AI Analysis System")
    print("=" * 50)
    
    # Initialize unified engine
    engine = UnifiedArchitecturalEngine()
    
    print("✓ Unified engine initialized successfully")
    print("System is ready for analysis")
    
    # Example usage (you can modify this based on your needs)
    # engine.analyze_architecture("path/to/your/image.jpg")

if __name__ == "__main__":
    main()
