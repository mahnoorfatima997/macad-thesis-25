#!/usr/bin/env python
"""
Test script for personality analysis integration
Validates that all components are working correctly
"""

import sys
import os
from pathlib import Path
import traceback

# Add project directories to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))
sys.path.append(str(project_root / "benchmarking"))

def test_imports():
    """Test that all personality analysis modules can be imported"""
    print("Testing imports...")
    
    try:
        from personality_models import PersonalityProfile, HEXACOModel
        print("✓ personality_models imported successfully")
    except Exception as e:
        print(f"✗ Failed to import personality_models: {e}")
        return False
    
    try:
        from personality_analyzer import PersonalityAnalyzer, create_analyzer_with_fallback
        print("✓ personality_analyzer imported successfully")
    except Exception as e:
        print(f"✗ Failed to import personality_analyzer: {e}")
        return False
    
    try:
        from personality_processor import PersonalityProcessor
        print("✓ personality_processor imported successfully")
    except Exception as e:
        print(f"✗ Failed to import personality_processor: {e}")
        return False
    
    try:
        from personality_visualizer import PersonalityVisualizer
        print("✓ personality_visualizer imported successfully")
    except Exception as e:
        print(f"✗ Failed to import personality_visualizer: {e}")
        return False
    
    try:
        from personality_dashboard import PersonalityDashboard
        print("✓ personality_dashboard imported successfully")
    except Exception as e:
        print(f"✗ Failed to import personality_dashboard: {e}")
        return False
    
    return True

def test_analyzer_initialization():
    """Test analyzer initialization and fallback mechanism"""
    print("\nTesting analyzer initialization...")
    
    try:
        from personality_analyzer import create_analyzer_with_fallback
        
        analyzer = create_analyzer_with_fallback()
        print(f"✓ Analyzer created: {analyzer.__class__.__name__}")
        print(f"  - BERT available: {analyzer.is_available}")
        print(f"  - Fallback enabled: {analyzer.use_fallback}")
        
        model_info = analyzer.get_model_info()
        print(f"  - Model: {model_info['model_name']}")
        print(f"  - Version: {model_info['analysis_version']}")
        
        return True
        
    except Exception as e:
        print(f"✗ Analyzer initialization failed: {e}")
        traceback.print_exc()
        return False

def test_text_analysis():
    """Test basic text analysis functionality"""
    print("\nTesting text analysis...")
    
    try:
        from personality_analyzer import create_analyzer_with_fallback
        
        analyzer = create_analyzer_with_fallback()
        
        # Test with sample text
        sample_text = """
        I really enjoy working on creative architectural projects that push boundaries and 
        explore new possibilities. I'm always curious about innovative materials and 
        unconventional design approaches. I prefer to work systematically and organize my 
        thoughts carefully before making decisions. I like collaborating with others and 
        value different perspectives. Sometimes I worry about making mistakes, but I try 
        to be thorough in my analysis. I believe in being honest and straightforward in 
        my communications with clients and colleagues.
        """
        
        print("Analyzing sample text...")
        profile = analyzer.analyze_text(sample_text)
        
        print(f"✓ Analysis completed")
        print(f"  - Session ID: {profile.session_id}")
        print(f"  - Text length: {profile.text_length} characters")
        print(f"  - Reliability score: {profile.reliability_score:.2f}")
        print(f"  - Analysis method: {profile.analysis_method}")
        print(f"  - Dominant traits: {profile.dominant_traits}")
        
        if profile.traits:
            print("  - Trait scores:")
            for trait, score in profile.traits.items():
                level = profile.levels.get(trait, 'unknown')
                print(f"    {trait}: {score:.2f} ({level})")
        
        return True
        
    except Exception as e:
        print(f"✗ Text analysis failed: {e}")
        traceback.print_exc()
        return False

def test_data_directories():
    """Test that required directories exist or can be created"""
    print("\nTesting data directories...")
    
    try:
        # Check thesis_data directory
        thesis_data_dir = project_root / "thesis_data"
        if thesis_data_dir.exists():
            print(f"✓ thesis_data directory found: {thesis_data_dir}")
            
            # Look for sample interaction files
            interaction_files = list(thesis_data_dir.glob("interactions_*.csv"))
            print(f"  - Found {len(interaction_files)} interaction files")
            
        else:
            print(f"⚠ thesis_data directory not found: {thesis_data_dir}")
        
        # Check/create results directories
        results_dir = project_root / "benchmarking" / "results" / "personality_reports"
        results_dir.mkdir(parents=True, exist_ok=True)
        print(f"✓ personality_reports directory ready: {results_dir}")
        
        viz_dir = project_root / "benchmarking" / "results" / "personality_visualizations"
        viz_dir.mkdir(parents=True, exist_ok=True)
        print(f"✓ personality_visualizations directory ready: {viz_dir}")
        
        return True
        
    except Exception as e:
        print(f"✗ Directory setup failed: {e}")
        return False

def test_asset_files():
    """Test that personality asset files are available"""
    print("\nTesting personality assets...")
    
    try:
        from personality_models import PersonalityAssetMapper
        
        asset_mapper = PersonalityAssetMapper()
        
        # Check if assets directory exists
        assets_dir = project_root / "assets" / "personality_features"
        if not assets_dir.exists():
            print(f"⚠ Assets directory not found: {assets_dir}")
            return False
        
        print(f"✓ Assets directory found: {assets_dir}")
        
        # Check for sample assets
        sample_assets = [
            "hexaco_openness_high.png",
            "hexaco_conscientiousness_medium.png",
            "hexaco_extraversion_low.png"
        ]
        
        for asset in sample_assets:
            asset_path = assets_dir / asset
            if asset_path.exists():
                print(f"  ✓ {asset}")
            else:
                print(f"  ⚠ {asset} not found")
        
        return True
        
    except Exception as e:
        print(f"✗ Asset testing failed: {e}")
        return False

def test_color_integration():
    """Test color scheme integration"""
    print("\nTesting color scheme integration...")
    
    try:
        from personality_models import PersonalityColorMapper
        from thesis_colors import THESIS_COLORS
        
        color_mapper = PersonalityColorMapper()
        
        print("✓ Color mapper initialized")
        print(f"  - Available thesis colors: {len(THESIS_COLORS)}")
        
        # Test trait color mapping
        sample_trait = "openness"
        trait_color = color_mapper.get_trait_color(sample_trait)
        print(f"  - {sample_trait} color: {trait_color}")
        
        # Test level color mapping  
        level_color = color_mapper.get_level_color("high")
        print(f"  - 'high' level color: {level_color}")
        
        return True
        
    except Exception as e:
        print(f"✗ Color integration failed: {e}")
        return False

def run_all_tests():
    """Run all validation tests"""
    print("="*60)
    print("PERSONALITY ANALYSIS INTEGRATION TEST")
    print("="*60)
    
    tests = [
        ("Module Imports", test_imports),
        ("Analyzer Initialization", test_analyzer_initialization), 
        ("Text Analysis", test_text_analysis),
        ("Data Directories", test_data_directories),
        ("Asset Files", test_asset_files),
        ("Color Integration", test_color_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "="*60)
    print("TEST RESULTS SUMMARY")
    print("="*60)
    
    passed = 0
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:<8} {test_name}")
        if result:
            passed += 1
    
    print(f"\nTotal: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All tests passed! Personality analysis integration is ready.")
    else:
        print(f"\n⚠ {len(results) - passed} test(s) failed. Please check the issues above.")
    
    print("\nNext steps:")
    print("1. Install missing dependencies: pip install -r personality_requirements.txt")
    print("2. Run the benchmarking pipeline: python benchmarking/run_benchmarking.py")
    print("3. Launch the dashboard: streamlit run benchmarking/benchmark_dashboard.py")

if __name__ == "__main__":
    run_all_tests()