#!/usr/bin/env python3
"""
Unified Architectural Analysis Engine
Coordinates all AI models for comprehensive architectural analysis
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

# Import our modular components
from detection.yolo_module import YOLODetector
from detection.sam_module import SAMSegmenter
from analysis.clip_blip_module import CLIPBLIPAnalyzer
from analysis.comprehensive_analysis import ComprehensiveArchitecturalAnalyzer

class UnifiedArchitecturalEngine:
    """Unified engine that coordinates all AI models for architectural analysis"""
    
    def __init__(self, output_dir: str = "output"):
        """
        Initialize the unified engine
        
        Args:
            output_dir (str): Directory to save analysis results
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize all modules
        print("🏗️ Initializing Unified Architectural Analysis Engine")
        print("=" * 60)
        
        # Detection modules
        self.yolo_detector = YOLODetector()
        self.sam_segmenter = SAMSegmenter()
        
        # Analysis modules
        self.clip_blip_analyzer = CLIPBLIPAnalyzer()
        self.comprehensive_analyzer = ComprehensiveArchitecturalAnalyzer()
        
        print("✓ All modules initialized successfully")
    
    def analyze_architecture(self, image_path: str, confidence_threshold: float = 0.5) -> Dict[str, Any]:
        """
        Perform comprehensive architectural analysis using all models
        
        Args:
            image_path (str): Path to the architectural image
            confidence_threshold (float): Minimum confidence for detections
            
        Returns:
            dict: Comprehensive analysis results from all models
        """
        print(f"\n🔍 Starting comprehensive analysis of: {Path(image_path).name}")
        print("=" * 60)
        
        # Validate input
        if not Path(image_path).exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        # Create timestamp for this analysis
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        analysis_id = f"unified_analysis_{timestamp}"
        
        # Create output subdirectory
        analysis_output_dir = self.output_dir / analysis_id
        analysis_output_dir.mkdir(exist_ok=True)
        
        results = {
            "analysis_id": analysis_id,
            "timestamp": timestamp,
            "input_image": image_path,
            "yolo_detection": {},
            "sam_segmentation": {},
            "clip_blip_analysis": {},
            "combined_analysis": {},
            "summary": {}
        }
        
        try:
            # Step 1: YOLO Detection
            print("Step 1: YOLO Object Detection...")
            yolo_results = self.yolo_detector.detect(image_path)
            results["yolo_detection"] = yolo_results
            
            if "error" not in yolo_results:
                print(f"✓ Detected {yolo_results['total_detections']} objects")
            else:
                print(f"⚠️ YOLO detection failed: {yolo_results['error']}")
            
            # Step 2: SAM Segmentation
            print("Step 2: SAM Segmentation...")
            sam_results = self.sam_segmenter.auto_segment(image_path, num_points=15)
            results["sam_segmentation"] = sam_results
            
            if "error" not in sam_results:
                print(f"✓ Generated {sam_results['total_segments']} segments")
            else:
                print(f"⚠️ SAM segmentation failed: {sam_results['error']}")
            
            # Step 3: CLIP/BLIP Analysis
            print("Step 3: CLIP/BLIP Visual Analysis...")
            clip_blip_results = self.clip_blip_analyzer.analyze_image(image_path)
            results["clip_blip_analysis"] = clip_blip_results
            
            if "error" not in clip_blip_results:
                print("✓ CLIP/BLIP analysis completed")
            else:
                print(f"⚠️ CLIP/BLIP analysis failed: {clip_blip_results['error']}")
            
            # Step 4: Comprehensive Analysis
            print("Step 4: Performing comprehensive analysis...")
            comprehensive_results = self.comprehensive_analyzer.analyze_architecture(
                yolo_results.get("detections", []),
                sam_results.get("segments", []),
                clip_blip_results
            )
            results["comprehensive_analysis"] = comprehensive_results
            
            # Step 5: Combine all analyses
            print("Step 5: Combining all analyses...")
            results["combined_analysis"] = self._combine_all_analyses(results)
            
            # Step 6: Generate comprehensive summary
            print("Step 6: Generating comprehensive summary...")
            results["summary"] = self._generate_comprehensive_summary(results)
            
            # Step 7: Generate visual outputs
            print("Step 7: Generating visual outputs...")
            self._generate_visual_outputs(results, analysis_output_dir, image_path)
            
            # Step 8: Generate detailed explanations
            print("Step 8: Generating detailed explanations...")
            results["detailed_explanation"] = self._generate_detailed_explanation(results)
            
            # Step 9: Save results
            results_file = analysis_output_dir / "unified_analysis_results.json"
            with open(results_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            
            # Step 10: Generate comprehensive report
            report_file = analysis_output_dir / "unified_analysis_report.txt"
            self._generate_comprehensive_report(results, report_file)
            
            print(f"\n✅ Comprehensive analysis completed successfully!")
            print(f"📁 Results saved to: {results_file}")
            print(f"📄 Report saved to: {report_file}")
            
            return results
            
        except Exception as e:
            print(f"❌ Error during analysis: {e}")
            # Save partial results if available
            if any(results[key] for key in ["yolo_detection", "sam_segmentation", "clip_blip_analysis"]):
                results["error"] = str(e)
                results_file = analysis_output_dir / "partial_analysis_results.json"
                with open(results_file, 'w') as f:
                    json.dump(results, f, indent=2, default=str)
                print(f"📁 Partial results saved to: {results_file}")
            raise
    
    def _generate_visual_outputs(self, results: Dict[str, Any], output_dir: Path, image_path: str):
        """Generate visual outputs including annotated images and segmentation maps"""
        try:
            import cv2
            import numpy as np
            from PIL import Image, ImageDraw, ImageFont
            
            # Load original image
            original_image = cv2.imread(image_path)
            if original_image is None:
                print("⚠️ Could not load image for visual output generation")
                return
            
            # 1. YOLO Detection Annotations
            yolo_results = results.get("yolo_detection", {})
            if "detections" in yolo_results and yolo_results["detections"]:
                yolo_annotated = original_image.copy()
                
                # Color palette for different classes
                colors = [
                    (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0),
                    (255, 0, 255), (0, 255, 255), (128, 0, 0), (0, 128, 0),
                    (0, 0, 128), (128, 128, 0), (128, 0, 128), (0, 128, 128)
                ]
                
                for i, detection in enumerate(yolo_results["detections"]):
                    bbox = detection["bbox"]
                    class_name = detection["class_name"]
                    confidence = detection["confidence"]
                    
                    # Draw bounding box
                    color = colors[i % len(colors)]
                    cv2.rectangle(yolo_annotated, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, 2)
                    
                    # Draw label
                    label = f"{class_name}: {confidence:.2f}"
                    label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
                    cv2.rectangle(yolo_annotated, (bbox[0], bbox[1] - label_size[1] - 10), 
                                (bbox[0] + label_size[0], bbox[1]), color, -1)
                    cv2.putText(yolo_annotated, label, (bbox[0], bbox[1] - 5), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                
                # Save YOLO annotated image
                yolo_output_path = output_dir / "yolo_detections.jpg"
                cv2.imwrite(str(yolo_output_path), yolo_annotated)
                print(f"📸 YOLO detections saved to: {yolo_output_path}")
            
            # 2. SAM Segmentation Visualization
            sam_results = results.get("sam_segmentation", {})
            if "segments" in sam_results and sam_results["segments"]:
                # Create segmentation overlay
                segmentation_overlay = np.zeros_like(original_image)
                
                for i, segment in enumerate(sam_results["segments"][:20]):  # Limit to first 20 segments
                    if "mask" in segment:
                        mask = segment["mask"]
                        if mask.shape[:2] == original_image.shape[:2]:
                            # Create colored mask
                            color = np.array(colors[i % len(colors)])
                            colored_mask = np.zeros_like(original_image)
                            colored_mask[mask] = color
                            
                            # Blend with overlay
                            alpha = 0.3
                            segmentation_overlay = cv2.addWeighted(segmentation_overlay, 1, colored_mask, alpha, 0)
                
                # Combine with original image
                final_segmentation = cv2.addWeighted(original_image, 0.7, segmentation_overlay, 0.3, 0)
                
                # Save SAM segmentation
                sam_output_path = output_dir / "sam_segmentation.jpg"
                cv2.imwrite(str(sam_output_path), final_segmentation)
                print(f"🎯 SAM segmentation saved to: {sam_output_path}")
            
            # 3. Combined Analysis Visualization
            combined_image = original_image.copy()
            
            # Add YOLO detections
            if "detections" in yolo_results and yolo_results["detections"]:
                for i, detection in enumerate(yolo_results["detections"]):
                    bbox = detection["bbox"]
                    class_name = detection["class_name"]
                    color = colors[i % len(colors)]
                    cv2.rectangle(combined_image, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, 2)
            
            # Add text overlay with key insights
            clip_blip_results = results.get("clip_blip_analysis", {})
            if "analysis" in clip_blip_results:
                analysis = clip_blip_results["analysis"]
                insights = analysis.get("combined_insights", {})
                
                # Create text overlay
                text_lines = [
                    f"Image Analysis Summary",
                    f"Architectural Style: {', '.join(insights.get('architectural_style', {}).keys())[:50]}",
                    f"Key Characteristics: {', '.join(insights.get('key_characteristics', [])[:3])}",
                    f"Total Elements Detected: {results.get('combined_analysis', {}).get('total_elements_detected', 0)}"
                ]
                
                # Draw text background
                text_height = len(text_lines) * 30 + 20
                cv2.rectangle(combined_image, (10, 10), (600, text_height), (0, 0, 0), -1)
                cv2.rectangle(combined_image, (10, 10), (600, text_height), (255, 255, 255), 2)
                
                # Draw text
                for i, line in enumerate(text_lines):
                    y_pos = 35 + i * 30
                    cv2.putText(combined_image, line, (20, y_pos), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Save combined visualization
            combined_output_path = output_dir / "combined_analysis.jpg"
            cv2.imwrite(str(combined_output_path), combined_image)
            print(f"🎨 Combined analysis saved to: {combined_output_path}")
            
        except Exception as e:
            print(f"⚠️ Error generating visual outputs: {e}")
    
    def _generate_detailed_explanation(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate detailed explanation of the architectural image"""
        explanation = {
            "image_overview": "",
            "architectural_elements": [],
            "design_analysis": {},
            "functional_analysis": {},
            "style_characteristics": {},
            "recommendations": [],
            "technical_details": {}
        }
        
        # Get CLIP/BLIP analysis
        clip_blip_results = results.get("clip_blip_analysis", {})
        if "analysis" in clip_blip_results:
            analysis = clip_blip_results["analysis"]
            insights = analysis.get("combined_insights", {})
            
            # Image overview from BLIP caption
            explanation["image_overview"] = analysis.get("blip_caption", "Architectural drawing or plan")
            
            # Style characteristics
            style_scores = insights.get("architectural_style", {})
            explanation["style_characteristics"] = {
                "primary_style": max(style_scores.items(), key=lambda x: x[1])[0] if style_scores else "unknown",
                "style_confidence": max(style_scores.values()) if style_scores else 0.0,
                "all_styles": style_scores
            }
            
            # Design analysis
            design_scores = insights.get("design_quality", {})
            explanation["design_analysis"] = {
                "overall_quality": sum(design_scores.values()) / len(design_scores) if design_scores else 0.0,
                "quality_aspects": design_scores
            }
            
            # Functional analysis
            functional_scores = insights.get("functional_aspects", {})
            explanation["functional_analysis"] = {
                "circulation_quality": functional_scores.get("good circulation", 0.0),
                "lighting_quality": functional_scores.get("natural lighting", 0.0),
                "organization_quality": functional_scores.get("well organized", 0.0),
                "all_functional_aspects": functional_scores
            }
        
        # Get YOLO detections
        yolo_results = results.get("yolo_detection", {})
        if "detections" in yolo_results:
            detected_elements = []
            for detection in yolo_results["detections"]:
                element = {
                    "type": detection["class_name"],
                    "confidence": detection["confidence"],
                    "location": detection["bbox"],
                    "area": detection["area"]
                }
                detected_elements.append(element)
            explanation["architectural_elements"] = detected_elements
        
        # Generate recommendations
        recommendations = []
        
        # Based on detected elements
        element_types = [elem["type"] for elem in explanation["architectural_elements"]]
        if "wall" in element_types and "door" not in element_types:
            recommendations.append("Consider adding doors for better circulation")
        if "window" not in element_types:
            recommendations.append("Consider adding windows for natural lighting")
        
        # Based on design quality
        design_quality = explanation["design_analysis"].get("overall_quality", 0.0)
        if design_quality < 0.5:
            recommendations.append("Consider improving overall design quality")
        
        # Based on functional aspects
        circulation = explanation["functional_analysis"].get("circulation_quality", 0.0)
        if circulation < 0.5:
            recommendations.append("Improve circulation patterns")
        
        explanation["recommendations"] = recommendations
        
        # Technical details
        explanation["technical_details"] = {
            "total_elements_detected": len(explanation["architectural_elements"]),
            "segments_generated": results.get("sam_segmentation", {}).get("total_segments", 0),
            "analysis_confidence": results.get("summary", {}).get("analysis_overview", {}).get("successful_analyses", 0) / 3.0
        }
        
        return explanation

    def _combine_all_analyses(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Combine insights from all analysis modules"""
        combined = {
            "total_elements_detected": 0,
            "key_insights": [],
            "design_quality_score": 0.0,
            "architectural_style": [],
            "critical_issues": [],
            "recommendations": [],
            "compliance_status": "unknown"
        }
        
        # YOLO insights
        yolo_results = results.get("yolo_detection", {})
        if "detections" in yolo_results:
            combined["total_elements_detected"] = len(yolo_results["detections"])
            combined["key_insights"].append(f"Detected {len(yolo_results['detections'])} architectural elements")
        
        # CLIP/BLIP insights
        clip_blip_results = results.get("clip_blip_analysis", {})
        if "analysis" in clip_blip_results:
            analysis = clip_blip_results["analysis"]
            insights = analysis.get("combined_insights", {})
            
            combined["architectural_style"] = list(insights.get("architectural_style", {}).keys())
            combined["key_insights"].extend(insights.get("key_characteristics", []))
            
            # Calculate design quality score
            summary = self.clip_blip_analyzer.get_analysis_summary(analysis)
            combined["design_quality_score"] = summary.get("overall_score", 0.0)
        
        # Note: GPT-4 and criticism modules were removed during consolidation
        # Focus on YOLO, SAM, and CLIP/BLIP analysis results
        
        return combined
    
    def _generate_comprehensive_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive summary of all results"""
        summary = {
            "analysis_overview": {},
            "key_findings": [],
            "model_performance": {},
            "recommendations": [],
            "risk_assessment": "unknown"
        }
        
        # Analysis overview
        summary["analysis_overview"] = {
            "total_models_used": 3,
            "successful_analyses": 0,
            "failed_analyses": 0
        }
        
        # Count successful vs failed analyses
        for key in ["yolo_detection", "sam_segmentation", "clip_blip_analysis"]:
            if key in results and "error" not in results[key]:
                summary["analysis_overview"]["successful_analyses"] += 1
            else:
                summary["analysis_overview"]["failed_analyses"] += 1
        
        # Key findings
        combined = results.get("combined_analysis", {})
        summary["key_findings"] = combined.get("key_insights", [])
        summary["recommendations"] = combined.get("recommendations", [])
        
        # Risk assessment based on critical issues
        critical_issues = combined.get("critical_issues", [])
        if len(critical_issues) > 5:
            summary["risk_assessment"] = "high"
        elif len(critical_issues) > 2:
            summary["risk_assessment"] = "medium"
        else:
            summary["risk_assessment"] = "low"
        
        return summary
    
    def _generate_comprehensive_report(self, results: Dict[str, Any], report_path: Path):
        """Generate comprehensive text report with detailed analysis"""
        try:
            with open(report_path, 'w') as f:
                f.write("=" * 100 + "\n")
                f.write("COMPREHENSIVE ARCHITECTURAL ANALYSIS REPORT\n")
                f.write("=" * 100 + "\n\n")
                
                f.write(f"Analysis ID: {results.get('analysis_id', 'N/A')}\n")
                f.write(f"Timestamp: {results.get('timestamp', 'N/A')}\n")
                f.write(f"Input Image: {results.get('input_image', 'N/A')}\n\n")
                
                # Executive Summary
                summary = results.get("summary", {})
                f.write("EXECUTIVE SUMMARY\n")
                f.write("-" * 30 + "\n")
                f.write(f"Risk Assessment: {summary.get('risk_assessment', 'unknown').upper()}\n")
                f.write(f"Successful Analyses: {summary.get('analysis_overview', {}).get('successful_analyses', 0)}/3\n")
                
                # Overall Assessment from Comprehensive Analysis
                comprehensive = results.get("comprehensive_analysis", {})
                if comprehensive:
                    overall = comprehensive.get("overall_assessment", {})
                    if overall:
                        f.write(f"Overall Score: {overall.get('total_score', 0):.1f}/100\n")
                        f.write(f"Risk Level: {overall.get('risk_level', 'unknown').upper()}\n")
                        f.write(f"Total Issues Identified: {len(comprehensive.get('critical_issues', []))}\n")
                        f.write(f"Total Recommendations: {len(comprehensive.get('recommendations', []))}\n")
                f.write("\n")
                
                # Detailed YOLO Detection Results
                yolo_results = results.get("yolo_detection", {})
                f.write("YOLO DETECTION RESULTS\n")
                f.write("-" * 30 + "\n")
                if "error" not in yolo_results:
                    detections = yolo_results.get("detections", [])
                    f.write(f"Total Elements Detected: {len(detections)}\n")
                    f.write(f"Model Used: {yolo_results.get('model_path', 'N/A')}\n")
                    f.write(f"Confidence Threshold: {yolo_results.get('confidence_threshold', 0)}\n\n")
                    
                    if detections:
                        f.write("DETECTED ELEMENTS:\n")
                        f.write("-" * 20 + "\n")
                        for i, detection in enumerate(detections, 1):
                            f.write(f"{i}. {detection['class_name'].upper()}\n")
                            f.write(f"   Confidence: {detection['confidence']:.3f} ({detection['confidence']*100:.1f}%)\n")
                            f.write(f"   Location: {detection['bbox']}\n")
                            # Handle area formatting - it might be a string
                            area = detection['area']
                            try:
                                area = float(area) if isinstance(area, str) else area
                                f.write(f"   Area: {area:.0f} pixels\n\n")
                            except (ValueError, TypeError):
                                f.write(f"   Area: {area} pixels\n\n")
                else:
                    f.write(f"YOLO Detection Failed: {yolo_results['error']}\n\n")
                
                # CLIP/BLIP Analysis Results
                clip_blip_results = results.get("clip_blip_analysis", {})
                f.write("CLIP/BLIP ANALYSIS RESULTS\n")
                f.write("-" * 30 + "\n")
                if "error" not in clip_blip_results:
                    analysis = clip_blip_results.get("analysis", {})
                    f.write(f"Image Description: {analysis.get('blip_caption', 'N/A')}\n\n")
                    
                    # CLIP Concepts Analysis
                    clip_concepts = analysis.get("clip_concepts", {})
                    if clip_concepts:
                        f.write("DETECTED CONCEPTS (Top 10):\n")
                        f.write("-" * 25 + "\n")
                        # Sort concepts by confidence and show top 10
                        sorted_concepts = sorted(clip_concepts.items(), key=lambda x: x[1], reverse=True)[:10]
                        for concept, confidence in sorted_concepts:
                            f.write(f"• {concept.replace('_', ' ').title()}: {confidence:.6f}\n")
                        f.write("\n")
                    
                    # Combined Insights
                    insights = analysis.get("combined_insights", {})
                    if insights:
                        f.write("KEY INSIGHTS:\n")
                        f.write("-" * 15 + "\n")
                        key_characteristics = insights.get("key_characteristics", [])
                        if key_characteristics:
                            f.write("Key Characteristics:\n")
                            for char in key_characteristics:
                                f.write(f"  - {char.replace('_', ' ').title()}\n")
                        f.write("\n")
                else:
                    f.write(f"CLIP/BLIP Analysis Failed: {clip_blip_results['error']}\n\n")
                
                # SAM Segmentation Results
                sam_results = results.get("sam_segmentation", {})
                f.write("SAM SEGMENTATION RESULTS\n")
                f.write("-" * 30 + "\n")
                if "error" not in sam_results:
                    segments = sam_results.get("segments", [])
                    f.write(f"Total Segments Generated: {len(segments)}\n")
                    f.write(f"Segmentation Method: {sam_results.get('method', 'auto')}\n")
                    f.write(f"Number of Points Used: {sam_results.get('num_points', 'N/A')}\n\n")
                    
                    if segments:
                        f.write("SEGMENT DETAILS (First 10):\n")
                        f.write("-" * 25 + "\n")
                        for i, segment in enumerate(segments[:10], 1):
                            segment_type = segment.get("type", "unknown")
                            confidence = segment.get("confidence", 0)
                            area = segment.get("area", 0)
                            # Handle area formatting - it might be a string
                            try:
                                area = float(area) if isinstance(area, str) else area
                                f.write(f"{i}. Type: {segment_type}, Confidence: {confidence:.3f}, Area: {area:.0f} pixels\n")
                            except (ValueError, TypeError):
                                f.write(f"{i}. Type: {segment_type}, Confidence: {confidence:.3f}, Area: {area} pixels\n")
                        f.write("\n")
                else:
                    f.write(f"SAM Segmentation Failed: {sam_results['error']}\n\n")
                
                # Comprehensive Analysis Results
                if comprehensive:
                    f.write("COMPREHENSIVE ANALYSIS RESULTS\n")
                    f.write("-" * 40 + "\n")
                    
                    # Spatial Analysis
                    spatial = comprehensive.get("spatial_analysis", {})
                    if spatial:
                        f.write("SPATIAL ANALYSIS:\n")
                        f.write("-" * 20 + "\n")
                        f.write(f"Circulation Efficiency: {spatial.get('circulation_efficiency', 0):.1f}/100\n")
                        f.write(f"Density Calculation: {spatial.get('density_calculation', 0):.1f}/100\n")
                        
                        # Adjacency Analysis
                        adjacency = spatial.get("adjacency_analysis", {})
                        if adjacency:
                            f.write(f"Adjacency Score: {adjacency.get('score', 0):.1f}/100\n")
                            f.write(f"Kitchen-Dining Adjacency: {'YES' if adjacency.get('kitchen_dining') else 'NO'}\n")
                            f.write(f"Bathroom Present: {'YES' if adjacency.get('bathroom_present') else 'NO'}\n")
                            f.write(f"Corridor Present: {'YES' if adjacency.get('corridor_present') else 'NO'}\n")
                            
                            # Detailed adjacency analysis
                            details = adjacency.get("details", {})
                            if details:
                                f.write("Detailed Adjacency Analysis:\n")
                                for key, value in details.items():
                                    if isinstance(value, dict):
                                        present = value.get("present", False)
                                        score = value.get("score", 0)
                                        f.write(f"  - {key.replace('_', ' ').title()}: {'YES' if present else 'NO'} (Score: {score:.1f})\n")
                                    else:
                                        f.write(f"  - {key.replace('_', ' ').title()}: {value}\n")
                        
                        # Proportional Analysis
                        proportional = spatial.get("proportional_analysis", {})
                        if proportional:
                            f.write("Proportional Analysis:\n")
                            area_consistency = proportional.get('area_consistency', 0)
                            avg_size = proportional.get('average_element_size', 0)
                            size_var = proportional.get('size_variation', 0)
                            
                            # Handle string values from JSON
                            try:
                                area_consistency = float(area_consistency) if isinstance(area_consistency, str) else area_consistency
                                avg_size = float(avg_size) if isinstance(avg_size, str) else avg_size
                                size_var = float(size_var) if isinstance(size_var, str) else size_var
                            except (ValueError, TypeError):
                                area_consistency = 0
                                avg_size = 0
                                size_var = 0
                            
                            f.write(f"  Area Consistency: {area_consistency}%\n")
                            f.write(f"  Average Element Size: {avg_size:.0f} pixels\n")
                            f.write(f"  Size Variation: {size_var:.3f}\n")
                            
                            # Room size distribution
                            room_sizes = proportional.get("room_size_distribution", {})
                            if room_sizes:
                                f.write("  Room Size Distribution:\n")
                                for room_type, details in room_sizes.items():
                                    if isinstance(details, dict):
                                        count = details.get("count", 0)
                                        avg_size = details.get("avg_size", 0)
                                        size_var = details.get("size_variation", 0)
                                        
                                        # Handle string values
                                        try:
                                            avg_size = float(avg_size) if isinstance(avg_size, str) else avg_size
                                            size_var = float(size_var) if isinstance(size_var, str) else size_var
                                        except (ValueError, TypeError):
                                            avg_size = 0
                                            size_var = 0
                                        
                                        f.write(f"    - {room_type}: {count} rooms, avg {avg_size:.0f} pixels, variation {size_var:.3f}\n")
                                    else:
                                        f.write(f"    - {room_type}: {details}\n")
                        
                        # Spatial Relationships
                        spatial_rel = spatial.get("spatial_relationships", {})
                        if spatial_rel:
                            f.write("Spatial Relationships:\n")
                            proximity = spatial_rel.get("proximity_analysis", {})
                            if proximity:
                                f.write(f"  Average Distance: {proximity.get('average_distance', 0):.1f} pixels\n")
                                f.write(f"  Distance Variation: {proximity.get('distance_variation', 0):.1f}\n")
                                f.write(f"  Closest Elements: {proximity.get('closest_elements', 0):.1f} pixels\n")
                                f.write(f"  Farthest Elements: {proximity.get('farthest_elements', 0):.1f} pixels\n")
                            
                            f.write(f"  Layout Pattern: {spatial_rel.get('layout_pattern', 'unknown')}\n")
                            f.write(f"  Spatial Efficiency: {spatial_rel.get('spatial_efficiency', 0):.1f}/100\n")
                        
                        # Room Distribution
                        room_dist = spatial.get("room_distribution", {})
                        if room_dist:
                            f.write(f"Total Rooms: {room_dist.get('total_rooms', 0)}\n")
                            f.write(f"Functional Balance: {room_dist.get('functional_balance', 0):.1f}%\n")
                            room_types = room_dist.get("room_types", {})
                            if room_types:
                                f.write("Room Type Distribution:\n")
                                for room_type, count in room_types.items():
                                    f.write(f"  - {room_type}: {count}\n")
                        
                        # Spatial Issues and Recommendations
                        spatial_issues = spatial.get("issues", [])
                        if spatial_issues:
                            f.write("Spatial Issues:\n")
                            for issue in spatial_issues:
                                f.write(f"  - {issue}\n")
                        
                        spatial_recs = spatial.get("recommendations", [])
                        if spatial_recs:
                            f.write("Spatial Recommendations:\n")
                            for rec in spatial_recs:
                                f.write(f"  - {rec}\n")
                        f.write("\n")
                    
                    # Functional Analysis
                    functional = comprehensive.get("functional_analysis", {})
                    if functional:
                        f.write("FUNCTIONAL ANALYSIS:\n")
                        f.write("-" * 20 + "\n")
                        f.write(f"Room Functionality: {functional.get('room_functionality', 0):.1f}/100\n")
                        f.write(f"Accessibility: {functional.get('accessibility', 0):.1f}/100\n")
                        f.write(f"Lighting Quality: {functional.get('lighting_quality', 0):.1f}/100\n")
                        f.write(f"Ventilation: {functional.get('ventilation', 0):.1f}/100\n")
                        f.write(f"Functional Efficiency: {functional.get('functional_efficiency', 0):.1f}/100\n")
                        
                        # Space Utilization Details
                        space_util = functional.get("space_utilization", {})
                        if space_util:
                            f.write("Space Utilization Details:\n")
                            for room_type, details in space_util.items():
                                f.write(f"  - {room_type}:\n")
                                f.write(f"    Count: {details.get('count', 0)}\n")
                                f.write(f"    Avg Confidence: {details.get('avg_confidence', 0):.3f}\n")
                                
                                # Handle string values for areas
                                total_area = details.get('total_area', 0)
                                avg_area = details.get('avg_area', 0)
                                try:
                                    total_area = float(total_area) if isinstance(total_area, str) else total_area
                                    avg_area = float(avg_area) if isinstance(avg_area, str) else avg_area
                                except (ValueError, TypeError):
                                    total_area = 0
                                    avg_area = 0
                                
                                f.write(f"    Total Area: {total_area:.0f} pixels\n")
                                f.write(f"    Avg Area: {avg_area:.0f} pixels\n")
                        
                        # Functional Issues and Recommendations
                        functional_issues = functional.get("issues", [])
                        if functional_issues:
                            f.write("Functional Issues:\n")
                            for issue in functional_issues:
                                f.write(f"  - {issue}\n")
                        
                        functional_recs = functional.get("recommendations", [])
                        if functional_recs:
                            f.write("Functional Recommendations:\n")
                            for rec in functional_recs:
                                f.write(f"  - {rec}\n")
                        f.write("\n")
                    
                    # Technical Analysis
                    technical = comprehensive.get("technical_analysis", {})
                    if technical:
                        f.write("TECHNICAL ANALYSIS:\n")
                        f.write("-" * 20 + "\n")
                        f.write(f"Structural Integrity: {technical.get('structural_integrity', 0):.1f}/100\n")
                        f.write(f"Code Compliance: {technical.get('code_compliance', 0):.1f}/100\n")
                        f.write(f"Energy Efficiency: {technical.get('energy_efficiency', 0):.1f}/100\n")
                        
                        material_analysis = technical.get("material_analysis", {})
                        if material_analysis:
                            f.write(f"Material Diversity: {material_analysis.get('material_diversity', 0):.1f}/100\n")
                            materials = material_analysis.get("materials_detected", [])
                            if materials:
                                f.write(f"Materials Detected: {', '.join(materials)}\n")
                        
                        # Technical Issues and Recommendations
                        technical_issues = technical.get("issues", [])
                        if technical_issues:
                            f.write("Technical Issues:\n")
                            for issue in technical_issues:
                                f.write(f"  - {issue}\n")
                        
                        technical_recs = technical.get("recommendations", [])
                        if technical_recs:
                            f.write("Technical Recommendations:\n")
                            for rec in technical_recs:
                                f.write(f"  - {rec}\n")
                        f.write("\n")
                    
                    # Aesthetic Analysis
                    aesthetic = comprehensive.get("aesthetic_analysis", {})
                    if aesthetic:
                        f.write("AESTHETIC ANALYSIS:\n")
                        f.write("-" * 20 + "\n")
                        f.write(f"Proportional Harmony: {aesthetic.get('proportional_harmony', 0):.1f}/100\n")
                        f.write(f"Visual Balance: {aesthetic.get('visual_balance', 0):.1f}/100\n")
                        f.write(f"Style Consistency: {aesthetic.get('style_consistency', 0):.1f}/100\n")
                        f.write(f"Contextual Fit: {aesthetic.get('contextual_fit', 0):.1f}/100\n")
                        
                        # Aesthetic Issues and Recommendations
                        aesthetic_issues = aesthetic.get("issues", [])
                        if aesthetic_issues:
                            f.write("Aesthetic Issues:\n")
                            for issue in aesthetic_issues:
                                f.write(f"  - {issue}\n")
                        
                        aesthetic_recs = aesthetic.get("recommendations", [])
                        if aesthetic_recs:
                            f.write("Aesthetic Recommendations:\n")
                            for rec in aesthetic_recs:
                                f.write(f"  - {rec}\n")
                        f.write("\n")
                    
                    # Accessibility Analysis
                    accessibility = comprehensive.get("accessibility_analysis", {})
                    if accessibility:
                        f.write("ACCESSIBILITY ANALYSIS:\n")
                        f.write("-" * 20 + "\n")
                        f.write(f"Wheelchair Accessibility: {accessibility.get('wheelchair_accessibility', 0):.1f}/100\n")
                        f.write(f"Wayfinding: {accessibility.get('wayfinding', 0):.1f}/100\n")
                        f.write(f"Clearance Spaces: {accessibility.get('clearance_spaces', 0):.1f}/100\n")
                        f.write(f"Ramp Access: {accessibility.get('ramp_access', 0):.1f}/100\n")
                        
                        # Accessibility Issues and Recommendations
                        accessibility_issues = accessibility.get("issues", [])
                        if accessibility_issues:
                            f.write("Accessibility Issues:\n")
                            for issue in accessibility_issues:
                                f.write(f"  - {issue}\n")
                        
                        accessibility_recs = accessibility.get("recommendations", [])
                        if accessibility_recs:
                            f.write("Accessibility Recommendations:\n")
                            for rec in accessibility_recs:
                                f.write(f"  - {rec}\n")
                        f.write("\n")
                    
                    # Sustainability Analysis
                    sustainability = comprehensive.get("sustainability_analysis", {})
                    if sustainability:
                        f.write("SUSTAINABILITY ANALYSIS:\n")
                        f.write("-" * 20 + "\n")
                        f.write(f"Energy Efficiency: {sustainability.get('energy_efficiency', 0):.1f}/100\n")
                        f.write(f"Sustainable Materials: {sustainability.get('sustainable_materials', 0):.1f}/100\n")
                        f.write(f"Site Response: {sustainability.get('site_response', 0):.1f}/100\n")
                        f.write(f"Passive Design: {sustainability.get('passive_design', 0):.1f}/100\n")
                        
                        # Sustainability Issues and Recommendations
                        sustainability_issues = sustainability.get("issues", [])
                        if sustainability_issues:
                            f.write("Sustainability Issues:\n")
                            for issue in sustainability_issues:
                                f.write(f"  - {issue}\n")
                        
                        sustainability_recs = sustainability.get("recommendations", [])
                        if sustainability_recs:
                            f.write("Sustainability Recommendations:\n")
                            for rec in sustainability_recs:
                                f.write(f"  - {rec}\n")
                        f.write("\n")
                    
                    # Circulation Analysis
                    circulation = comprehensive.get("circulation_analysis", {})
                    if circulation:
                        f.write("CIRCULATION ANALYSIS:\n")
                        f.write("-" * 20 + "\n")
                        f.write(f"Circulation Efficiency: {circulation.get('circulation_efficiency', 0):.1f}/100\n")
                        f.write(f"Connectivity: {circulation.get('connectivity', 0):.1f}/100\n")
                        
                        flow_patterns = circulation.get("flow_patterns", {})
                        if flow_patterns:
                            f.write("Flow Patterns:\n")
                            for pattern, present in flow_patterns.items():
                                f.write(f"  - {pattern}: {'YES' if present else 'NO'}\n")
                        
                        # Circulation Issues and Recommendations
                        circulation_issues = circulation.get("issues", [])
                        if circulation_issues:
                            f.write("Circulation Issues:\n")
                            for issue in circulation_issues:
                                f.write(f"  - {issue}\n")
                        
                        circulation_recs = circulation.get("recommendations", [])
                        if circulation_recs:
                            f.write("Circulation Recommendations:\n")
                            for rec in circulation_recs:
                                f.write(f"  - {rec}\n")
                        f.write("\n")
                    
                    # Lighting Analysis
                    lighting = comprehensive.get("lighting_analysis", {})
                    if lighting:
                        f.write("LIGHTING ANALYSIS:\n")
                        f.write("-" * 20 + "\n")
                        f.write(f"Natural Lighting: {lighting.get('natural_lighting', 0):.1f}/100\n")
                        f.write(f"Artificial Lighting: {lighting.get('artificial_lighting', 0):.1f}/100\n")
                        f.write(f"Glare Control: {lighting.get('glare_control', 0):.1f}/100\n")
                        f.write(f"Light Distribution: {lighting.get('light_distribution', 0):.1f}/100\n")
                        
                        # Lighting Issues and Recommendations
                        lighting_issues = lighting.get("issues", [])
                        if lighting_issues:
                            f.write("Lighting Issues:\n")
                            for issue in lighting_issues:
                                f.write(f"  - {issue}\n")
                        
                        lighting_recs = lighting.get("recommendations", [])
                        if lighting_recs:
                            f.write("Lighting Recommendations:\n")
                            for rec in lighting_recs:
                                f.write(f"  - {rec}\n")
                        f.write("\n")
                    
                    # Acoustics Analysis
                    acoustics = comprehensive.get("acoustics_analysis", {})
                    if acoustics:
                        f.write("ACOUSTICS ANALYSIS:\n")
                        f.write("-" * 20 + "\n")
                        f.write(f"Sound Isolation: {acoustics.get('sound_isolation', 0):.1f}/100\n")
                        f.write(f"Echo Control: {acoustics.get('echo_control', 0):.1f}/100\n")
                        f.write(f"Acoustic Comfort: {acoustics.get('acoustic_comfort', 0):.1f}/100\n")
                        f.write(f"Noise Control: {acoustics.get('noise_control', 0):.1f}/100\n\n")
                    
                    # Thermal Analysis
                    thermal = comprehensive.get("thermal_analysis", {})
                    if thermal:
                        f.write("THERMAL ANALYSIS:\n")
                        f.write("-" * 20 + "\n")
                        f.write(f"Thermal Comfort: {thermal.get('thermal_comfort', 0):.1f}/100\n")
                        f.write(f"Insulation: {thermal.get('insulation', 0):.1f}/100\n")
                        f.write(f"Thermal Bridges: {thermal.get('thermal_bridges', 0):.1f}/100\n")
                        f.write(f"Climate Response: {thermal.get('climate_response', 0):.1f}/100\n\n")
                
                # Critical Issues
                critical_issues = comprehensive.get("critical_issues", []) if comprehensive else []
                if critical_issues:
                    f.write("CRITICAL ISSUES\n")
                    f.write("-" * 20 + "\n")
                    for i, issue in enumerate(critical_issues, 1):
                        f.write(f"{i}. {issue}\n")
                    f.write("\n")
                
                # Recommendations
                recommendations = comprehensive.get("recommendations", []) if comprehensive else []
                if recommendations:
                    f.write("RECOMMENDATIONS\n")
                    f.write("-" * 20 + "\n")
                    for i, rec in enumerate(recommendations, 1):
                        f.write(f"{i}. {rec}\n")
                    f.write("\n")
                
                # Detailed Explanation
                detailed_explanation = results.get("detailed_explanation", {})
                if detailed_explanation:
                    f.write("DETAILED EXPLANATION\n")
                    f.write("-" * 20 + "\n")
                    f.write(f"Image Overview: {detailed_explanation.get('image_overview', 'N/A')}\n\n")
                    
                    # Style Analysis
                    style = detailed_explanation.get("style_characteristics", {})
                    if style and style.get("primary_style") != "unknown":
                        f.write("STYLE ANALYSIS:\n")
                        f.write("-" * 15 + "\n")
                        f.write(f"Primary Style: {style.get('primary_style')}\n")
                        f.write(f"Style Confidence: {style.get('style_confidence', 0):.3f}\n\n")
                    
                    # Functional Analysis
                    functional = detailed_explanation.get("functional_analysis", {})
                    if functional:
                        f.write("FUNCTIONAL QUALITY:\n")
                        f.write("-" * 15 + "\n")
                        f.write(f"Circulation Quality: {functional.get('circulation_quality', 0):.3f}\n")
                        f.write(f"Lighting Quality: {functional.get('lighting_quality', 0):.3f}\n")
                        f.write(f"Organization Quality: {functional.get('organization_quality', 0):.3f}\n\n")
                    
                    # Technical Details
                    technical = detailed_explanation.get("technical_details", {})
                    if technical:
                        f.write("TECHNICAL DETAILS:\n")
                        f.write("-" * 15 + "\n")
                        f.write(f"Total Elements Detected: {technical.get('total_elements_detected', 0)}\n")
                        f.write(f"Segments Generated: {technical.get('segments_generated', 0)}\n")
                        f.write(f"Analysis Confidence: {technical.get('analysis_confidence', 0):.3f}\n\n")
                
                # Model Performance Summary
                f.write("MODEL PERFORMANCE SUMMARY\n")
                f.write("-" * 30 + "\n")
                
                # YOLO Performance
                yolo_results = results.get("yolo_detection", {})
                if "error" not in yolo_results:
                    f.write(f"YOLO Detection: SUCCESS - {yolo_results.get('total_detections', 0)} elements detected\n")
                else:
                    f.write(f"YOLO Detection: FAILED - {yolo_results['error']}\n")
                
                # SAM Performance
                sam_results = results.get("sam_segmentation", {})
                if "error" not in sam_results:
                    f.write(f"SAM Segmentation: SUCCESS - {sam_results.get('total_segments', 0)} segments generated\n")
                else:
                    f.write(f"SAM Segmentation: FAILED - {sam_results['error']}\n")
                
                # CLIP/BLIP Performance
                clip_blip_results = results.get("clip_blip_analysis", {})
                if "error" not in clip_blip_results:
                    f.write("CLIP/BLIP Analysis: SUCCESS - Completed successfully\n")
                else:
                    f.write(f"CLIP/BLIP Analysis: FAILED - {clip_blip_results['error']}\n")
                
                f.write("\n" + "=" * 100 + "\n")
                f.write("END OF COMPREHENSIVE ARCHITECTURAL ANALYSIS REPORT\n")
                f.write("=" * 100 + "\n")
                
        except Exception as e:
            print(f"Error generating report: {e}")
    
    def print_analysis_summary(self, results: Dict[str, Any]):
        """Print a formatted analysis summary to console"""
        print("\n" + "="*80)
        print("UNIFIED ARCHITECTURAL ANALYSIS SUMMARY")
        print("="*80)
        
        # Basic info
        print(f"Analysis ID: {results.get('analysis_id', 'N/A')}")
        print(f"Timestamp: {results.get('timestamp', 'N/A')}")
        print(f"Input Image: {results.get('input_image', 'N/A')}")
        print()
        
        # Summary
        summary = results.get("summary", {})
        risk_assessment = summary.get("risk_assessment", "unknown").upper()
        successful_analyses = summary.get("analysis_overview", {}).get("successful_analyses", 0)
        
        print("EXECUTIVE SUMMARY:")
        print("-" * 20)
        print(f"Risk Assessment: {risk_assessment}")
        print(f"Successful Analyses: {successful_analyses}/3")
        
        # Key findings
        key_findings = summary.get("key_findings", [])
        if key_findings:
            print(f"\nKEY FINDINGS ({len(key_findings)}):")
            print("-" * 15)
            for finding in key_findings[:5]:  # Show top 5
                print(f"• {finding}")
        
        # Critical issues
        combined = results.get("combined_analysis", {})
        critical_issues = combined.get("critical_issues", [])
        if critical_issues:
            print(f"\nCRITICAL ISSUES ({len(critical_issues)}):")
            print("-" * 20)
            for issue in critical_issues[:3]:  # Show top 3
                print(f"• {issue}")
        
        # Comprehensive Analysis Results
        comprehensive = results.get("comprehensive_analysis", {})
        if comprehensive:
            print(f"\n🏗️ COMPREHENSIVE ANALYSIS:")
            print("-" * 30)
            
            # Overall Assessment
            overall = comprehensive.get("overall_assessment", {})
            if overall:
                print(f"Overall Score: {overall.get('total_score', 0):.1f}/100")
                print(f"Risk Level: {overall.get('risk_level', 'unknown').upper()}")
            
            # Key Analysis Categories
            categories = [
                ("Spatial", "spatial_analysis"),
                ("Functional", "functional_analysis"), 
                ("Technical", "technical_analysis"),
                ("Aesthetic", "aesthetic_analysis"),
                ("Accessibility", "accessibility_analysis"),
                ("Sustainability", "sustainability_analysis"),
                ("Circulation", "circulation_analysis"),
                ("Lighting", "lighting_analysis")
            ]
            
            print(f"\n📊 ANALYSIS CATEGORIES:")
            print("-" * 25)
            for name, key in categories:
                if key in comprehensive:
                    analysis = comprehensive[key]
                    if "circulation_efficiency" in analysis:
                        score = analysis["circulation_efficiency"]
                        print(f"{name}: {score:.1f}/100")
                    elif "room_functionality" in analysis:
                        score = analysis["room_functionality"]
                        print(f"{name}: {score:.1f}/100")
                    elif "structural_integrity" in analysis:
                        score = analysis["structural_integrity"]
                        print(f"{name}: {score:.1f}/100")
                    elif "proportional_harmony" in analysis:
                        score = analysis["proportional_harmony"]
                        print(f"{name}: {score:.1f}/100")
        
        # Critical Issues
        critical_issues = comprehensive.get("critical_issues", []) if comprehensive else []
        if critical_issues:
            print(f"\n🚨 CRITICAL ISSUES ({len(critical_issues)}):")
            print("-" * 25)
            for issue in critical_issues[:5]:  # Show top 5
                print(f"• {issue}")
        
        # Detailed explanation
        detailed_explanation = results.get("detailed_explanation", {})
        if detailed_explanation:
            print(f"\n📝 DETAILED EXPLANATION:")
            print("-" * 25)
            print(f"Image Overview: {detailed_explanation.get('image_overview', 'N/A')}")
            
            # Style analysis
            style = detailed_explanation.get("style_characteristics", {})
            if style.get("primary_style") != "unknown":
                print(f"Primary Style: {style.get('primary_style')} (confidence: {style.get('style_confidence', 0):.2f})")
            
            # Functional analysis
            functional = detailed_explanation.get("functional_analysis", {})
            if functional:
                print(f"Circulation Quality: {functional.get('circulation_quality', 0):.2f}")
                print(f"Lighting Quality: {functional.get('lighting_quality', 0):.2f}")
                print(f"Organization Quality: {functional.get('organization_quality', 0):.2f}")
            
            # Recommendations
            recommendations = detailed_explanation.get("recommendations", [])
            if recommendations:
                print(f"\n💡 RECOMMENDATIONS ({len(recommendations)}):")
                print("-" * 20)
                for rec in recommendations[:3]:  # Show top 3
                    print(f"• {rec}")
        
        print("\n" + "="*80) 


if __name__ == "__main__":
    """Main entry point for direct execution"""
    import sys
    
    # Add src to path for imports
    current_dir = Path(__file__).parent
    src_dir = current_dir.parent.parent
    sys.path.insert(0, str(src_dir))
    
    # Check command line arguments
    if len(sys.argv) < 2:
        print("Usage: python unified_engine.py <image_path>")
        print("Example: python unified_engine.py ./datasets/raw/sample_plan.jpg")
        sys.exit(1)
    
    # Get image path from command line
    image_path = sys.argv[1]
    
    # Initialize and run analysis
    try:
        engine = UnifiedArchitecturalEngine()
        results = engine.analyze_architecture(image_path)
        engine.print_analysis_summary(results)
        print(f"\n✅ Analysis complete! Check the 'output' directory for detailed results.")
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        sys.exit(1) 