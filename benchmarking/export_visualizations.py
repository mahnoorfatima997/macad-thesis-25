#!/usr/bin/env python
"""
Standalone script to export all visualizations from existing benchmark results
"""

import sys
from pathlib import Path
from export_all_visualizations import BenchmarkVisualizationExporter


def main():
    """Export visualizations from existing benchmark results"""
    
    # Check if results directory exists
    results_path = Path("benchmarking/results")
    if not results_path.exists():
        print("Error: No benchmark results found!")
        print("Please run the benchmarking tool first: python benchmarking/run_benchmarking.py")
        sys.exit(1)
    
    # Check if we have evaluation reports
    eval_reports = list((results_path / "evaluation_reports").glob("*.json"))
    if not eval_reports:
        print("Error: No evaluation reports found!")
        print("Please run the benchmarking tool first.")
        sys.exit(1)
    
    print("="*60)
    print("BENCHMARK VISUALIZATION EXPORT")
    print("="*60)
    print(f"\nFound {len(eval_reports)} evaluation reports")
    print("Starting export process...\n")
    
    try:
        # Create exporter and export all visualizations
        exporter = BenchmarkVisualizationExporter()
        exporter.export_all_visualizations()
        
        print("\n" + "="*60)
        print("SUCCESS!")
        print("="*60)
        print(f"\nVisualizations exported to: {results_path / 'visualizations'}")
        print(f"Open index.html to browse all visualizations")
        
    except Exception as e:
        print(f"\nError during export: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()