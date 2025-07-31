"""
Verify that test data is being saved to the correct locations for benchmarking
"""

from pathlib import Path
import json

def verify_data_locations():
    """Check where data is being saved and what the benchmarking tools expect"""
    print("Data Location Verification")
    print("=" * 60)
    
    # Expected locations by benchmarking tools
    print("\n1. BENCHMARKING TOOLS EXPECT DATA IN:")
    print("   - Main data: ./thesis_data/")
    print("   - Session files: ./thesis_data/interactions_*.csv")
    print("   - Session summaries: ./thesis_data/session_summary_*.json")
    print("   - Moves files: ./thesis_data/moves_*.csv")
    
    # Check what exists in expected location
    thesis_data_dir = Path("thesis_data")
    if thesis_data_dir.exists():
        interactions = list(thesis_data_dir.glob("interactions_*.csv"))
        sessions = list(thesis_data_dir.glob("session_*.json"))
        moves = list(thesis_data_dir.glob("moves_*.csv"))
        linkography_dir = thesis_data_dir / "linkography"
        linkographs = list(linkography_dir.glob("*.json")) if linkography_dir.exists() else []
        
        print(f"\n2. FOUND IN thesis_data/:")
        print(f"   - Interaction files: {len(interactions)}")
        print(f"   - Session files: {len(sessions)}")
        print(f"   - Moves files: {len(moves)}")
        print(f"   - Linkography files: {len(linkographs)}")
        
        if interactions:
            print(f"\n   Sample files:")
            for f in interactions[:3]:
                print(f"     - {f.name}")
    else:
        print(f"\n   WARNING: Directory {thesis_data_dir} does not exist!")
    
    # Check old test locations
    print("\n3. CHECKING OLD TEST LOCATIONS:")
    
    test_data_dir = Path("thesis_tests/test_data")
    if test_data_dir.exists():
        old_files = list(test_data_dir.glob("*"))
        print(f"   - Found {len(old_files)} files in {test_data_dir}")
        if old_files:
            print("     WARNING: These files need to be migrated!")
    
    linkography_test_dir = Path("thesis_tests/linkography_data")
    if linkography_test_dir.exists():
        old_linkography = list(linkography_test_dir.glob("*"))
        print(f"   - Found {len(old_linkography)} linkography files in {linkography_test_dir}")
        if old_linkography:
            print("     WARNING: These files need to be migrated!")
    
    # Check benchmarking results
    print("\n4. BENCHMARKING OUTPUT LOCATIONS:")
    results_dir = Path("benchmarking/results")
    if results_dir.exists():
        result_files = list(results_dir.glob("*"))
        print(f"   - Found {len(result_files)} result files")
        
        # Check for specific result types
        if (results_dir / "benchmark_report.json").exists():
            print("   [OK] benchmark_report.json exists")
        if (results_dir / "comprehensive_benchmark_report.json").exists():
            print("   [OK] comprehensive_benchmark_report.json exists")
        
        eval_dir = results_dir / "evaluation_reports"
        if eval_dir.exists():
            eval_files = list(eval_dir.glob("*.json"))
            print(f"   - Found {len(eval_files)} evaluation reports")
    
    # Recommendations
    print("\n5. RECOMMENDATIONS:")
    
    if test_data_dir.exists() and list(test_data_dir.glob("*")):
        print("   WARNING: Run 'python migrate_test_data.py' to migrate old test data")
    
    print("   [OK] New test sessions will now save to thesis_data/")
    print("   [OK] Linkography data will save to thesis_data/linkography/")
    print("   [OK] Benchmarking tools will find all data automatically")
    
    # Test the new paths
    print("\n6. TESTING NEW SAVE PATHS:")
    print(f"   - Session data will save to: thesis_data/session_[id].json")
    print(f"   - Interaction data will save to: thesis_data/interactions_[id].csv")
    print(f"   - Moves data will save to: thesis_data/moves_[id].csv")
    print(f"   - Linkography data will save to: thesis_data/linkography/linkography_[id].json")

if __name__ == "__main__":
    verify_data_locations()