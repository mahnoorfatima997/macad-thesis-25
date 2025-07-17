#!/usr/bin/env python3
"""
Site Plan Analysis Application
Integrates YOLO object detection, OpenCV shape detection, and GPT-4 Vision semantic analysis for comprehensive site plan evaluation
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, Any, Optional

# Set up E drive environment first
from utils.e_drive_setup import setup_e_drive_environment
setup_e_drive_environment()

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scripts.preprocess import preprocess_for_analysis
from scripts.detect_yolo import analyze_site_plan_elements, draw_detections_on_image
from scripts.shape_detection import analyze_site_plan_structures, detect_shapes_in_site_plan, shape_analyzer
from scripts.gpt4_vision_analysis import analyze_site_plan_semantics, generate_design_recommendations, gpt4_analyzer
from utils.file_utils import ensure_directory_exists

class SitePlanAnalyzer:
    def __init__(self, output_dir: str = "output"):
        """
        Initialize the site plan analyzer
        
        Args:
            output_dir (str): Directory to save analysis results
        """
        self.output_dir = output_dir
        ensure_directory_exists(output_dir)
        
        # Set up E drive cache
        self.e_cache_dir = setup_e_drive_environment()
        print(f"✓ Using E drive cache: {self.e_cache_dir}")
        
    def analyze_site_plan(self, image_path: str, confidence_threshold: float = 0.5) -> Dict[str, Any]:
        """
        Complete analysis pipeline for a site plan
        
        Args:
            image_path (str): Path to the site plan image
            confidence_threshold (float): Minimum confidence for YOLO detections
            
        Returns:
            dict: Complete analysis results
        """
        print(f"Starting analysis of: {image_path}")
        print(f"Using E drive for all model storage and cache")
        
        # Validate input
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        # Create timestamp for this analysis
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        analysis_id = f"analysis_{timestamp}"
        
        # Create output subdirectory for this analysis
        analysis_output_dir = os.path.join(self.output_dir, analysis_id)
        ensure_directory_exists(analysis_output_dir)
        
        results = {
            "analysis_id": analysis_id,
            "timestamp": timestamp,
            "input_image": image_path,
            "cache_location": self.e_cache_dir,
            "preprocessing": {},
            "object_detection": {},
            "semantic_analysis": {},
            "summary": {}
        }
        
        try:
            # Step 1: Preprocessing
            print("Step 1: Preprocessing image...")
            preprocessed_image = preprocess_for_analysis(
                image_path, 
                output_path=os.path.join(analysis_output_dir, "preprocessed.jpg")
            )
            results["preprocessing"]["status"] = "completed"
            results["preprocessing"]["output_path"] = os.path.join(analysis_output_dir, "preprocessed.jpg")
            
            # Step 2: Object Detection with YOLO
            print("Step 2: Performing object detection...")
            detection_results = analyze_site_plan_elements(image_path, confidence_threshold)
            results["object_detection"] = detection_results
            
            # Draw detections on image
            annotated_image_path = os.path.join(analysis_output_dir, "annotated_detections.jpg")
            draw_detections_on_image(image_path, detection_results, annotated_image_path)
            results["object_detection"]["annotated_image"] = annotated_image_path
            
            # Step 3: Shape Detection
            print("Step 3: Performing shape detection...")
            shape_results = detect_shapes_in_site_plan(image_path)
            results["shape_detection"] = shape_results
            
            # Create annotated shape detection image
            shape_annotated_path = os.path.join(analysis_output_dir, "shape_detections.jpg")
            shape_analyzer.create_annotated_image(image_path, shape_annotated_path)
            results["shape_detection"]["annotated_image"] = shape_annotated_path
            
            # Step 4: Semantic Analysis with GPT-4 Vision
            print("Step 4: Performing semantic analysis with GPT-4 Vision...")
            semantic_results = analyze_site_plan_semantics(image_path)
            results["semantic_analysis"] = semantic_results
            
            # Step 5: Generate design recommendations
            print("Step 5: Generating design recommendations...")
            design_recommendations = generate_design_recommendations(image_path)
            results["semantic_analysis"]["design_recommendations"] = design_recommendations
            
            # Step 6: Enhanced analysis with YOLO context
            print("Step 6: Performing enhanced analysis with YOLO context...")
            enhanced_analysis = gpt4_analyzer.analyze_with_yolo_context(image_path, detection_results)
            results["semantic_analysis"]["enhanced_analysis"] = enhanced_analysis
            
            # Step 7: Create summary
            print("Step 7: Creating analysis summary...")
            results["summary"] = self._create_summary(detection_results, shape_results, semantic_results)
            
            # Step 8: Clean up temporary files
            print("Step 8: Cleaning up temporary files...")
            gpt4_analyzer.cleanup_temp_files()
            
            # Save results
            results_file = os.path.join(analysis_output_dir, "analysis_results.json")
            with open(results_file, 'w') as f:
                json.dump(results, f, indent=2)
            
            print(f"Analysis completed successfully!")
            print(f"Results saved to: {results_file}")
            print(f"All models and cache stored on E drive: {self.e_cache_dir}")
            
            return results
            
        except Exception as e:
            print(f"Error during analysis: {e}")
            # Save partial results if available
            if results.get("preprocessing") or results.get("object_detection"):
                results["error"] = str(e)
                results_file = os.path.join(analysis_output_dir, "analysis_results_partial.json")
                with open(results_file, 'w') as f:
                    json.dump(results, f, indent=2)
                print(f"Partial results saved to: {results_file}")
            raise
    
    def _create_summary(self, detection_results: Dict[str, Any], shape_results: Dict[str, Any], semantic_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a summary of the analysis results
        
        Args:
            detection_results (dict): YOLO detection results
            shape_results (dict): Shape detection results
            semantic_results (dict): GPT-4 Vision semantic analysis results
            
        Returns:
            dict: Summary of key findings
        """
        summary = {
            "key_findings": [],
            "detection_summary": {},
            "shape_analysis": {},
            "semantic_insights": {},
            "storage_info": {
                "cache_location": self.e_cache_dir,
                "models_stored_on": "E drive"
            }
        }
        
        # Extract key findings from detections
        if detection_results.get("summary"):
            detection_summary = detection_results["summary"]
            summary["detection_summary"] = {
                "total_elements": detection_summary.get("total_detections", 0),
                "high_confidence_elements": detection_summary.get("high_confidence_detections", 0),
                "element_types": detection_summary.get("detection_summary", {})
            }
            
            # Add key findings from detections
            for element_type, count in detection_summary.get("detection_summary", {}).items():
                if count > 0:
                    summary["key_findings"].append(f"Detected {count} {element_type}(s)")
        
        # Extract key findings from shape detection
        if shape_results and not shape_results.get("error"):
            summary["shape_analysis"] = {
                "total_shapes": shape_results.get("total_shapes", 0),
                "shape_types": shape_results.get("shapes_by_type", {}),
                "size_distribution": shape_results.get("processing_info", {})
            }
            
            # Add key findings from shape detection
            if shape_results.get("total_shapes", 0) > 0:
                summary["key_findings"].append(f"Detected {shape_results['total_shapes']} geometric shapes")
                
                # Add specific shape findings
                for shape_type, count in shape_results.get("shapes_by_type", {}).items():
                    if count > 0:
                        summary["key_findings"].append(f"Found {count} {shape_type}(s)")
        
        # Extract key insights from semantic analysis
        if semantic_results:
            summary["semantic_insights"] = {
                "spatial_constraints_identified": bool(semantic_results.get("spatial_constraints")),
                "building_analysis_completed": bool(semantic_results.get("building_elements")),
                "site_features_analyzed": bool(semantic_results.get("site_features")),
                "circulation_evaluated": bool(semantic_results.get("access_circulation")),
                "zoning_assessed": bool(semantic_results.get("zoning_compliance")),
                "recommendations_generated": bool(semantic_results.get("design_recommendations"))
            }
            
            # Add key findings from semantic analysis
            if semantic_results.get("spatial_constraints"):
                summary["key_findings"].append("Spatial constraints and design issues identified")
            if semantic_results.get("design_recommendations"):
                summary["key_findings"].append("Design recommendations provided")
        
        return summary
    
    def print_analysis_report(self, results: Dict[str, Any]):
        """
        Print a formatted analysis report
        
        Args:
            results (dict): Analysis results
        """
        print("\n" + "="*80)
        print("SITE PLAN ANALYSIS REPORT")
        print("="*80)
        
        print(f"\nAnalysis ID: {results.get('analysis_id', 'N/A')}")
        print(f"Timestamp: {results.get('timestamp', 'N/A')}")
        print(f"Input Image: {results.get('input_image', 'N/A')}")
        print(f"Cache Location: {results.get('cache_location', 'N/A')}")
        
        # Object Detection Summary
        if results.get("object_detection", {}).get("summary"):
            detection_summary = results["object_detection"]["summary"]
            print(f"\n📊 OBJECT DETECTION RESULTS:")
            print(f"   Total elements detected: {detection_summary.get('total_detections', 0)}")
            print(f"   High confidence detections: {detection_summary.get('high_confidence_detections', 0)}")
            
            if detection_summary.get("detection_summary"):
                print("   Element breakdown:")
                for element, count in detection_summary["detection_summary"].items():
                    print(f"     • {element}: {count}")
        
        # Shape Detection Summary
        if results.get("shape_detection") and not results["shape_detection"].get("error"):
            shape_summary = results["shape_detection"]
            print(f"\n🔷 SHAPE DETECTION RESULTS:")
            print(f"   Total shapes detected: {shape_summary.get('total_shapes', 0)}")
            
            if shape_summary.get("shapes_by_type"):
                print("   Shape breakdown:")
                for shape_type, count in shape_summary["shapes_by_type"].items():
                    print(f"     • {shape_type}: {count}")
        
        # Semantic Analysis Summary
        if results.get("semantic_analysis"):
            print(f"\n🧠 SEMANTIC ANALYSIS RESULTS:")
            semantic_results = results["semantic_analysis"]
            
            if semantic_results.get("spatial_constraints"):
                print("   ✓ Spatial constraints analyzed")
            if semantic_results.get("building_elements"):
                print("   ✓ Building elements identified")
            if semantic_results.get("site_features"):
                print("   ✓ Site features evaluated")
            if semantic_results.get("access_circulation"):
                print("   ✓ Access and circulation assessed")
            if semantic_results.get("zoning_compliance"):
                print("   ✓ Zoning compliance reviewed")
            if semantic_results.get("design_recommendations"):
                print("   ✓ Design recommendations generated")
        
        # Key Findings
        if results.get("summary", {}).get("key_findings"):
            print(f"\n🔍 KEY FINDINGS:")
            for finding in results["summary"]["key_findings"]:
                print(f"   • {finding}")
        
        # Storage Information
        if results.get("summary", {}).get("storage_info"):
            storage_info = results["summary"]["storage_info"]
            print(f"\n💾 STORAGE INFORMATION:")
            print(f"   Cache Location: {storage_info.get('cache_location', 'N/A')}")
            print(f"   Models Stored: {storage_info.get('models_stored_on', 'N/A')}")
        
        print("\n" + "="*80)
        print("Analysis completed successfully!")
        print("All models and cache stored on E drive to save C drive space!")
        print("="*80)


def main():
    """Main function to run the site plan analysis"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Site Plan Analysis Tool")
    parser.add_argument("image_path", help="Path to the site plan image")
    parser.add_argument("--confidence", type=float, default=0.5, 
                       help="Confidence threshold for YOLO detections (default: 0.5)")
    parser.add_argument("--output-dir", default="output", 
                       help="Output directory for results (default: output)")
    
    args = parser.parse_args()
    
    # Check if E drive exists
    if not os.path.exists("E:/"):
        print("❌ Error: E drive not found!")
        print("Please ensure E drive is available and accessible.")
        print("The system is configured to use E drive for all model storage.")
        sys.exit(1)
    
    # Check if OpenAI API key is set
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  Warning: OPENAI_API_KEY environment variable not set.")
        print("   GPT-4 Vision analysis will not work without an API key.")
        print("   Please set your OpenAI API key:")
        print("   export OPENAI_API_KEY='your-api-key-here'")
        print("   or create a .env file with: OPENAI_API_KEY=your-api-key-here")
        print()
    
    try:
        # Initialize analyzer
        analyzer = SitePlanAnalyzer(output_dir=args.output_dir)
        
        # Run analysis
        results = analyzer.analyze_site_plan(args.image_path, args.confidence)
        
        # Print report
        analyzer.print_analysis_report(results)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
