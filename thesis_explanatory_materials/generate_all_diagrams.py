#!/usr/bin/env python3
"""
MEGA Architectural Mentor - Master Diagram Generator

This script regenerates all thesis explanatory diagrams using the thesis color palette.
Run this script whenever you need to update all visualizations with consistent styling.

Usage:
    python generate_all_diagrams.py [--output-dir PATH] [--format PNG|SVG|BOTH]

Author: MEGA Architectural Mentor Development Team
Date: August 2025
"""

import os
import sys
import argparse
import importlib.util
from pathlib import Path
import time
from typing import List, Optional

def load_and_execute_diagram_script(script_path: Path, output_dir: Optional[Path] = None) -> bool:
    """
    Load and execute a diagram generation script.
    
    Args:
        script_path: Path to the Python script
        output_dir: Optional output directory override
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Add the script directory to Python path
        script_dir = script_path.parent
        if str(script_dir) not in sys.path:
            sys.path.insert(0, str(script_dir))
        
        # Load the module
        spec = importlib.util.spec_from_file_location(script_path.stem, script_path)
        if spec is None or spec.loader is None:
            print(f"ERROR: Could not load module from {script_path}")
            return False
            
        module = importlib.util.module_from_spec(spec)
        
        # Execute the module to define functions
        spec.loader.exec_module(module)
        
        # Call the save_diagram function if it exists
        if hasattr(module, 'save_diagram'):
            print(f"Generating {script_path.name}...")
            start_time = time.time()
            module.save_diagram()
            end_time = time.time()
            print(f"SUCCESS: {script_path.name} completed in {end_time - start_time:.2f}s")
            return True
        else:
            print(f"ERROR: {script_path.name} does not have a save_diagram function")
            return False
            
    except Exception as e:
        print(f"ERROR executing {script_path.name}: {str(e)}")
        return False
    finally:
        # Clean up the path
        if str(script_dir) in sys.path:
            sys.path.remove(str(script_dir))

def find_diagram_scripts(diagrams_dir: Path) -> List[Path]:
    """
    Find all diagram generation scripts in the diagrams directory.
    
    Args:
        diagrams_dir: Path to the diagrams directory
        
    Returns:
        List of Python script paths, sorted numerically
    """
    scripts = []
    
    # Look for numbered diagram scripts
    for i in range(1, 20):  # Support up to 20 diagrams
        for prefix in [f"{i:02d}_", f"0{i}_", f"{i}_"]:
            pattern = f"{prefix}*.py"
            matches = list(diagrams_dir.glob(pattern))
            scripts.extend(matches)
    
    # Remove duplicates and sort
    scripts = list(set(scripts))
    scripts.sort()
    
    return scripts

def verify_dependencies():
    """Verify that required dependencies are available."""
    required_packages = [
        'matplotlib',
        'numpy',
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("ERROR: Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nPlease install missing packages using:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_thesis_colors_availability(diagrams_dir: Path) -> bool:
    """Check if thesis_colors.py is accessible."""
    # Look for thesis_colors.py in the expected location
    thesis_colors_path = diagrams_dir.parent.parent / 'benchmarking' / 'thesis_colors.py'
    
    if not thesis_colors_path.exists():
        print(f"ERROR: thesis_colors.py not found at {thesis_colors_path}")
        print("   This file is required for consistent color theming.")
        return False
    
    print(f"SUCCESS: thesis_colors.py found at {thesis_colors_path}")
    return True

def generate_summary_report(successful_diagrams: List[str], failed_diagrams: List[str], 
                          output_dir: Path) -> None:
    """Generate a summary report of the diagram generation process."""
    
    report_path = output_dir / "generation_report.md"
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# MEGA Architectural Mentor - Diagram Generation Report\n\n")
        f.write(f"Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## Summary\n\n")
        f.write(f"- **Total diagrams**: {len(successful_diagrams) + len(failed_diagrams)}\n")
        f.write(f"- **Successful**: {len(successful_diagrams)}\n")
        f.write(f"- **Failed**: {len(failed_diagrams)}\n\n")
        
        if successful_diagrams:
            f.write("## Successfully Generated Diagrams\n\n")
            for diagram in successful_diagrams:
                f.write(f"- SUCCESS: {diagram}\n")
            f.write("\n")
        
        if failed_diagrams:
            f.write("## Failed Diagrams\n\n")
            for diagram in failed_diagrams:
                f.write(f"- FAILED: {diagram}\n")
            f.write("\n")
        
        f.write("## Diagram Descriptions\n\n")
        diagram_descriptions = {
            "01_system_architecture": "Complete system architecture showing all components and their interactions",
            "02_data_flow_pipeline": "Data flow from user interaction to final reports",
            "03_cognitive_metrics_flow": "Visual representation of cognitive metric calculations",
            "04_benchmarking_pipeline": "9-step benchmarking process flowchart",
            "05_agent_orchestration": "Multi-agent system workflow and coordination",
            "06_linkography_analysis": "Design move analysis and linkography patterns",
            "07_comparative_framework": "3-group comparison methodology framework",
            "08_dashboard_structure": "Dashboard sections and component overview"
        }
        
        for diagram_key, description in diagram_descriptions.items():
            status = "SUCCESS" if any(diagram_key in d for d in successful_diagrams) else "FAILED"
            f.write(f"### {status}: {diagram_key.replace('_', ' ').title()}\n")
            f.write(f"{description}\n\n")
        
        f.write("## File Formats Generated\n\n")
        f.write("Each successful diagram is saved in two formats:\n")
        f.write("- **PNG**: High-resolution (300 DPI) for presentations and documents\n")
        f.write("- **SVG**: Vector format for scalable graphics and web use\n\n")
        
        f.write("## Color Palette\n\n")
        f.write("All diagrams use the consistent thesis color palette:\n")
        f.write("- Primary Dark: `#4f3a3e` (Dark burgundy)\n")
        f.write("- Primary Purple: `#5c4f73` (Deep purple)\n")
        f.write("- Primary Violet: `#784c80` (Rich violet)\n")
        f.write("- Primary Rose: `#b87189` (Dusty rose)\n")
        f.write("- Accent Coral: `#cd766d` (Coral red)\n")
        f.write("- Accent Magenta: `#cf436f` (Bright magenta)\n\n")
        
        f.write("## Usage Instructions\n\n")
        f.write("To regenerate all diagrams:\n")
        f.write("```bash\n")
        f.write("python generate_all_diagrams.py\n")
        f.write("```\n\n")
        f.write("To specify output directory:\n")
        f.write("```bash\n")
        f.write("python generate_all_diagrams.py --output-dir /path/to/output\n")
        f.write("```\n\n")
    
    print(f"Generation report saved to: {report_path}")

def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Generate all MEGA Architectural Mentor thesis diagrams",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate_all_diagrams.py
  python generate_all_diagrams.py --output-dir ./custom_output
  python generate_all_diagrams.py --format PNG
        """
    )
    
    parser.add_argument(
        '--output-dir',
        type=Path,
        help='Output directory for generated diagrams (default: ./diagrams/)'
    )
    
    parser.add_argument(
        '--format',
        choices=['PNG', 'SVG', 'BOTH'],
        default='BOTH',
        help='Output format(s) (default: BOTH)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    # Determine paths
    script_dir = Path(__file__).parent
    diagrams_dir = args.output_dir or (script_dir / 'diagrams')
    
    # Ensure diagrams directory exists
    diagrams_dir.mkdir(parents=True, exist_ok=True)
    
    print("MEGA Architectural Mentor - Diagram Generator")
    print("=" * 50)
    print(f"Diagrams directory: {diagrams_dir.absolute()}")
    print(f"Output format: {args.format}")
    print()
    
    # Verify dependencies
    print("Checking dependencies...")
    if not verify_dependencies():
        sys.exit(1)
    
    # Check thesis colors availability
    if not check_thesis_colors_availability(diagrams_dir):
        sys.exit(1)
    
    # Find diagram scripts
    diagram_scripts = find_diagram_scripts(diagrams_dir)
    
    if not diagram_scripts:
        print("ERROR: No diagram scripts found in the diagrams directory!")
        print(f"   Expected location: {diagrams_dir}")
        print("   Looking for files matching patterns: 01_*.py, 02_*.py, etc.")
        sys.exit(1)
    
    print(f"Found {len(diagram_scripts)} diagram scripts:")
    for script in diagram_scripts:
        print(f"   - {script.name}")
    print()
    
    # Generate diagrams
    print("Starting diagram generation...")
    print("-" * 30)
    
    successful_diagrams = []
    failed_diagrams = []
    
    start_time = time.time()
    
    for script_path in diagram_scripts:
        if load_and_execute_diagram_script(script_path, diagrams_dir):
            successful_diagrams.append(script_path.name)
        else:
            failed_diagrams.append(script_path.name)
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # Generate summary
    print("\n" + "=" * 50)
    print("GENERATION SUMMARY")
    print("=" * 50)
    print(f"Total time: {total_time:.2f} seconds")
    print(f"Successful: {len(successful_diagrams)}/{len(diagram_scripts)}")
    print(f"Failed: {len(failed_diagrams)}/{len(diagram_scripts)}")
    
    if successful_diagrams:
        print("\nSuccessfully generated:")
        for diagram in successful_diagrams:
            print(f"   - {diagram}")
    
    if failed_diagrams:
        print("\nFailed to generate:")
        for diagram in failed_diagrams:
            print(f"   - {diagram}")
    
    # Generate report
    generate_summary_report(successful_diagrams, failed_diagrams, diagrams_dir)
    
    # Final status
    if failed_diagrams:
        print(f"\nGeneration completed with {len(failed_diagrams)} errors")
        sys.exit(1)
    else:
        print(f"\nAll {len(successful_diagrams)} diagrams generated successfully!")
        print(f"Output location: {diagrams_dir.absolute()}")

if __name__ == "__main__":
    main()