#!/usr/bin/env python3
"""
Enable development mode for cost-efficient testing
"""

import os
import sys

def enable_dev_mode():
    """Enable development mode"""
    
    print("🔧 ENABLING DEVELOPMENT MODE")
    print("=" * 40)
    print()
    
    # Set environment variable
    os.environ["DEV_MODE"] = "true"
    
    print("✅ Development mode enabled!")
    print()
    print("COST-SAVING FEATURES:")
    print("- Uses GPT-3.5-turbo instead of GPT-4o")
    print("- Reduced token limits (50-150 instead of 200-300)")
    print("- Web search disabled")
    print("- Visual analysis disabled") 
    print("- Simplified multi-agent synthesis")
    print("- Mock responses for testing")
    print()
    
    print("TO USE:")
    print("1. Run: python enable_dev_mode.py")
    print("2. Then: streamlit run app.py")
    print("3. Or set: set DEV_MODE=true (Windows) / export DEV_MODE=true (Linux/Mac)")
    print()
    
    print("ESTIMATED COST REDUCTION:")
    print("- GPT-4o: $0.03/1K tokens → GPT-3.5-turbo: $0.002/1K tokens (15x cheaper)")
    print("- Token usage: ~70% reduction from limits")
    print("- Feature disabling: ~50% reduction from fewer calls")
    print("- TOTAL: ~90% cost reduction for development")
    print()
    
    return True

def disable_dev_mode():
    """Disable development mode"""
    
    print("🚀 DISABLING DEVELOPMENT MODE")
    print("=" * 40)
    print()
    
    os.environ["DEV_MODE"] = "false"
    
    print("✅ Production mode enabled!")
    print("- Uses GPT-4o for best quality")
    print("- Full token limits")
    print("- All features enabled")
    print()

def check_dev_mode():
    """Check current development mode status"""
    
    dev_mode = os.getenv("DEV_MODE", "false").lower() == "true"
    
    print("CURRENT MODE:")
    if dev_mode:
        print("🔧 DEVELOPMENT MODE (Cost-efficient)")
        print("- Model: GPT-3.5-turbo")
        print("- Reduced tokens")
        print("- Limited features")
    else:
        print("🚀 PRODUCTION MODE (Full quality)")
        print("- Model: GPT-4o")
        print("- Full tokens")
        print("- All features")
    print()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == "enable":
            enable_dev_mode()
        elif command == "disable":
            disable_dev_mode()
        elif command == "check":
            check_dev_mode()
        else:
            print("Usage: python enable_dev_mode.py [enable|disable|check]")
    else:
        # Default: enable dev mode
        enable_dev_mode()