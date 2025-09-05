#!/usr/bin/env python3
"""
MEGA Architectural Mentor - Professional Diagram Generation Suite

This master script generates all professional-grade diagrams for the thesis-agents
system documentation. Each diagram features sophisticated visual effects, professional
styling, and publication-quality output suitable for academic presentations.
"""

import os
import sys
import subprocess
import time
from pathlib import Path

# Add current directory to path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Color palette for consistent branding
COLORS = {
    'primary_dark': '#4f3a3e',
    'primary_purple': '#5c4f73', 
    'primary_violet': '#784c80',
    'primary_rose': '#b87189',
    'accent_coral': '#cd766d',
    'accent_magenta': '#cf436f',
    'success_green': '#28a745',
    'warning_orange': '#fd7e14',
    'error_red': '#dc3545'
}

def print_header():
    """Print professional header"""
    print("=" * 80)
    print("🎨 MEGA ARCHITECTURAL MENTOR - PROFESSIONAL DIAGRAM SUITE")
    print("=" * 80)
    print("📊 Generating publication-quality diagrams with advanced visual effects")
    print("🎯 Features: Gradients, shadows, professional typography, interactive elements")
    print("📈 Output: High-resolution PNG, scalable SVG, academic PDF formats")
    print("-" * 80)

def print_status(message, status="info"):
    """Print colored status messages"""
    colors = {
        'info': '\033[94m',      # Blue
        'success': '\033[92m',   # Green
        'warning': '\033[93m',   # Yellow
        'error': '\033[91m',     # Red
        'reset': '\033[0m'       # Reset
    }
    
    icons = {
        'info': 'ℹ️',
        'success': '✅',
        'warning': '⚠️',
        'error': '❌'
    }
    
    color = colors.get(status, colors['info'])
    icon = icons.get(status, 'ℹ️')
    reset = colors['reset']
    
    print(f"{color}{icon} {message}{reset}")

def ensure_dependencies():
    """Ensure all required dependencies are available"""
    print_status("Checking dependencies...", "info")
    
    required_packages = [
        'matplotlib',
        'numpy',
        'pathlib'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print_status(f"✓ {package} available", "success")
        except ImportError:
            missing_packages.append(package)
            print_status(f"✗ {package} missing", "error")
    
    if missing_packages:
        print_status(f"Missing packages: {', '.join(missing_packages)}", "error")
        print_status("Please install missing packages with: pip install " + " ".join(missing_packages), "warning")
        return False
    
    return True

def create_output_directory():
    """Create output directory structure"""
    output_dir = Path("thesis_agents_explanatory_materials/diagrams")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print_status(f"Output directory: {output_dir.absolute()}", "info")
    return output_dir

def generate_diagram(script_name, description):
    """Generate a single diagram with error handling"""
    print_status(f"Generating {description}...", "info")
    
    try:
        # Import and execute the diagram script
        if script_name == "01_agentic_system_overview":
            from diagrams.agentic_system_overview import save_diagram
        elif script_name == "02_agent_interaction_flow":
            from diagrams.agent_interaction_flow import save_diagram
        elif script_name == "03_orchestration_workflow":
            from diagrams.orchestration_workflow import save_diagram
        else:
            print_status(f"Unknown script: {script_name}", "error")
            return False
        
        # Execute diagram generation
        start_time = time.time()
        save_diagram()
        end_time = time.time()
        
        print_status(f"✓ {description} completed in {end_time - start_time:.2f}s", "success")
        return True
        
    except ImportError as e:
        print_status(f"Import error for {script_name}: {e}", "error")
        return False
    except Exception as e:
        print_status(f"Generation error for {script_name}: {e}", "error")
        return False

def generate_all_diagrams():
    """Generate all professional diagrams"""
    
    # Diagram specifications
    diagrams = [
        ("01_agentic_system_overview", "Agentic System Architecture Overview"),
        ("02_agent_interaction_flow", "Multi-Agent Interaction Flow"),
        ("03_orchestration_workflow", "LangGraph Orchestration Workflow")
    ]
    
    successful = 0
    failed = 0
    
    print_status(f"Generating {len(diagrams)} professional diagrams...", "info")
    print("-" * 80)
    
    for script_name, description in diagrams:
        if generate_diagram(script_name, description):
            successful += 1
        else:
            failed += 1
        print("-" * 40)
    
    return successful, failed

def generate_diagram_report(successful, failed, total_time):
    """Generate comprehensive generation report"""
    
    print("=" * 80)
    print("📊 DIAGRAM GENERATION REPORT")
    print("=" * 80)
    
    print(f"✅ Successfully Generated: {successful} diagrams")
    print(f"❌ Failed: {failed} diagrams")
    print(f"⏱️  Total Time: {total_time:.2f} seconds")
    print(f"📁 Output Directory: thesis_agents_explanatory_materials/diagrams/")
    
    if successful > 0:
        print("\n🎯 Generated Diagram Features:")
        print("   • Advanced visual effects (gradients, shadows, 3D elements)")
        print("   • Professional typography and layout")
        print("   • Detailed component annotations and callouts")
        print("   • Dynamic connection lines showing data flow")
        print("   • Interactive legend and annotation systems")
        print("   • Multiple output formats (PNG, SVG, PDF)")
        print("   • Publication-quality resolution (300 DPI)")
        print("   • Consistent thesis branding and color palette")
        
        print("\n📈 Output Formats:")
        print("   • High-Resolution PNG (300 DPI) - For presentations and documents")
        print("   • Scalable Vector SVG - For web and interactive use")
        print("   • Academic PDF - For thesis and publication inclusion")
        
        print("\n🎨 Visual Enhancements:")
        print("   • Sophisticated gradient backgrounds")
        print("   • Professional shadow effects")
        print("   • Enhanced typography with text effects")
        print("   • Dynamic flow arrows and connections")
        print("   • Interactive elements and indicators")
        print("   • Comprehensive legends and annotations")
    
    if failed > 0:
        print(f"\n⚠️  {failed} diagrams failed to generate. Check error messages above.")
        print("   • Ensure all dependencies are installed")
        print("   • Check file permissions in output directory")
        print("   • Verify Python environment compatibility")
    
    print("\n" + "=" * 80)
    
    if successful == len([("01_agentic_system_overview", ""), ("02_agent_interaction_flow", ""), ("03_orchestration_workflow", "")]):
        print("🎉 ALL DIAGRAMS GENERATED SUCCESSFULLY!")
        print("📚 Ready for academic presentations and thesis documentation")
    else:
        print("⚠️  Some diagrams failed. Please review error messages and retry.")
    
    print("=" * 80)

def main():
    """Main execution function"""
    start_time = time.time()
    
    # Print header
    print_header()
    
    # Check dependencies
    if not ensure_dependencies():
        print_status("Dependency check failed. Exiting.", "error")
        return 1
    
    # Create output directory
    output_dir = create_output_directory()
    
    # Generate all diagrams
    successful, failed = generate_all_diagrams()
    
    # Calculate total time
    total_time = time.time() - start_time
    
    # Generate report
    generate_diagram_report(successful, failed, total_time)
    
    # Return appropriate exit code
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
