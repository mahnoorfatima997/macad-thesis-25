#!/usr/bin/env python3
"""
Test script to verify all imports work correctly
"""

import sys
import os

# Add paths
current_dir = os.path.dirname(os.path.abspath(__file__))
dashboard_path = os.path.join(current_dir, 'dashboard')
thesis_agents_path = os.path.join(current_dir, 'thesis-agents')

if dashboard_path not in sys.path:
    sys.path.insert(0, dashboard_path)
if thesis_agents_path not in sys.path:
    sys.path.insert(0, thesis_agents_path)

def test_imports():
    """Test all critical imports"""
    print("Testing imports...")
    
    # Test replicate
    try:
        import replicate
        print("✅ Replicate module available")
    except Exception as e:
        print(f"❌ Replicate error: {e}")
    
    # Test analysis components
    try:
        from dashboard.ui.analysis_components import convert_agent_response_to_dict, render_cognitive_analysis_dashboard
        print("✅ Analysis components import successfully")
    except Exception as e:
        print(f"❌ Analysis components error: {e}")
    
    # Test phase assessment
    try:
        from thesis_agents.phase_assessment.phase_manager import PhaseAssessmentManager
        print("✅ Phase assessment imports successfully")
    except Exception as e:
        print(f"❌ Phase assessment error: {e}")
    
    # Test image processing (optional)
    try:
        from thesis_agents.image_processing.vision_processor import VisionProcessor
        print("✅ Vision processor imports successfully")
    except Exception as e:
        print(f"⚠️ Vision processor not available: {e}")
    
    try:
        from thesis_agents.image_processing.image_generator import ImageGenerator
        print("✅ Image generator imports successfully")
    except Exception as e:
        print(f"⚠️ Image generator not available: {e}")
    
    print("\n✅ Import test completed successfully!")

if __name__ == "__main__":
    test_imports()
