#!/usr/bin/env python3
"""
ReCo Dataset Analyzer
Analyze the ReCo architectural dataset structure
"""

import json
import os
from pathlib import Path
import cv2
import numpy as np

def analyze_reco_dataset():
    """Analyze the ReCo dataset structure"""
    print("🔍 ANALYZING RECO DATASET")
    print("=" * 50)
    
    reco_path = Path("data/ReCo_geojson.json")
    
    if not reco_path.exists():
        print(f"❌ ReCo dataset not found at {reco_path}")
        return
    
    print(f"📁 Dataset size: {reco_path.stat().st_size / (1024**3):.2f} GB")
    
    # Read first few lines to understand structure
    with open(reco_path, 'r', encoding='utf-8') as f:
        # Read first 1000 characters to understand structure
        sample = f.read(1000)
        print(f"\n📋 Sample content:")
        print(sample[:500] + "...")
    
    # Try to parse as JSON to understand structure
    try:
        with open(reco_path, 'r', encoding='utf-8') as f:
            # Read first few lines to get structure
            first_line = f.readline().strip()
            if first_line.startswith('['):
                # Array format
                print(f"\n📊 Format: JSON Array")
                # Count lines to estimate number of entries
                f.seek(0)
                line_count = sum(1 for _ in f)
                print(f"📈 Estimated entries: {line_count}")
            else:
                print(f"\n📊 Format: Single JSON object")
    except Exception as e:
        print(f"❌ Error parsing JSON: {e}")
    
    return True

def analyze_sample_images():
    """Analyze the sample images"""
    print(f"\n🖼️ ANALYZING SAMPLE IMAGES")
    print("=" * 50)
    
    # Analyze sample_plan.jpg
    plan_path = Path("data/sample_plan.jpg")
    if plan_path.exists():
        img = cv2.imread(str(plan_path))
        if img is not None:
            h, w = img.shape[:2]
            print(f"📋 sample_plan.jpg:")
            print(f"   Size: {w}x{h} pixels")
            print(f"   File size: {plan_path.stat().st_size / 1024:.1f} KB")
            print(f"   Type: Floor plan (much better for architectural analysis!)")
            
            # Save a preview
            preview_path = "output/plan_preview.jpg"
            cv2.imwrite(preview_path, cv2.resize(img, (800, 600)))
            print(f"   Preview saved to: {preview_path}")
    
    # Analyze sample_elevation.jpg
    elevation_path = Path("data/sample_elevation.jpg")
    if elevation_path.exists():
        img = cv2.imread(str(elevation_path))
        if img is not None:
            h, w = img.shape[:2]
            print(f"\n📋 sample_elevation.jpg:")
            print(f"   Size: {w}x{h} pixels")
            print(f"   File size: {elevation_path.stat().st_size / 1024:.1f} KB")
            print(f"   Type: Building elevation")

def create_sam_enhanced_pipeline():
    """Create an enhanced pipeline that makes better use of SAM"""
    print(f"\n🚀 CREATING SAM-ENHANCED PIPELINE")
    print("=" * 50)
    
    enhanced_script = '''#!/usr/bin/env python3
"""
SAM-Enhanced Architectural Analysis Pipeline
Makes better use of SAM for architectural element detection
"""

import cv2
import numpy as np
from pathlib import Path
import json
from typing import List, Dict, Any, Tuple
import matplotlib.pyplot as plt
from segment_anything import SamPredictor, sam_model_registry
import torch

class SAMEnhancedArchitecturalAnalyzer:
    """Enhanced architectural analysis using SAM"""
    
    def __init__(self, sam_checkpoint_path: str = "src/models/sam/sam_vit_h_4b8939.pth"):
        self.sam_checkpoint_path = Path(sam_checkpoint_path)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Load SAM model
        if self.sam_checkpoint_path.exists():
            print(f"✓ Loading SAM model from {self.sam_checkpoint_path}")
            self.sam = sam_model_registry["vit_h"](checkpoint=str(self.sam_checkpoint_path))
            self.sam.to(device=self.device)
            self.predictor = SamPredictor(self.sam)
        else:
            print(f"❌ SAM model not found at {self.sam_checkpoint_path}")
            self.sam = None
            self.predictor = None
    
    def detect_architectural_elements_with_sam(self, image_path: str) -> Dict[str, Any]:
        """Detect architectural elements using SAM and computer vision"""
        print(f"🏗️ Analyzing {Path(image_path).name} with SAM")
        
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            return {"error": "Could not load image"}
        
        # Convert to RGB for SAM
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        results = {
            "image_path": image_path,
            "sam_detections": [],
            "cv_detections": [],
            "combined_analysis": {}
        }
        
        # Step 1: Computer Vision Pre-processing
        cv_results = self._cv_preprocessing(image)
        results["cv_detections"] = cv_results
        
        # Step 2: SAM-based Detection (if available)
        if self.predictor is not None:
            sam_results = self._sam_architectural_detection(image_rgb, cv_results)
            results["sam_detections"] = sam_results
        
        # Step 3: Combined Analysis
        results["combined_analysis"] = self._combine_detections(cv_results, results.get("sam_detections", []))
        
        return results
    
    def _cv_preprocessing(self, image: np.ndarray) -> Dict[str, Any]:
        """Computer vision preprocessing for architectural elements"""
        results = {
            "doors": [],
            "windows": [],
            "walls": [],
            "rooms": [],
            "shapes": []
        }
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Edge detection
        edges = cv2.Canny(gray, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Analyze contours for architectural elements
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < 100:  # Filter small noise
                continue
            
            # Get bounding rectangle
            x, y, w, h = cv2.boundingRect(contour)
            
            # Analyze shape characteristics
            aspect_ratio = w / h if h > 0 else 0
            contour_area = cv2.contourArea(contour)
            
            # Classify based on shape and size
            element = self._classify_architectural_element(x, y, w, h, aspect_ratio, contour_area, contour)
            if element:
                results[element["type"]].append(element)
        
        return results
    
    def _classify_architectural_element(self, x: int, y: int, w: int, h: int, 
                                      aspect_ratio: float, area: float, contour: np.ndarray) -> Dict[str, Any]:
        """Classify contour as architectural element"""
        
        # Door detection (typically rectangular, medium size)
        if 0.2 < aspect_ratio < 5.0 and 100 < area < 10000:
            # Check if it's door-like (rectangular, near bottom of image)
            if self._is_door_like(contour, aspect_ratio):
                return {
                    "type": "doors",
                    "bbox": [x, y, w, h],
                    "center": [x + w//2, y + h//2],
                    "confidence": 0.7,
                    "area": area,
                    "aspect_ratio": aspect_ratio
                }
        
        # Window detection (typically square-ish, smaller)
        if 0.5 < aspect_ratio < 2.0 and 50 < area < 5000:
            if self._is_window_like(contour, aspect_ratio):
                return {
                    "type": "windows",
                    "bbox": [x, y, w, h],
                    "center": [x + w//2, y + h//2],
                    "confidence": 0.6,
                    "area": area,
                    "aspect_ratio": aspect_ratio
                }
        
        # Wall detection (long, thin rectangles)
        if (aspect_ratio > 5.0 or aspect_ratio < 0.2) and area > 500:
            return {
                "type": "walls",
                "bbox": [x, y, w, h],
                "center": [x + w//2, y + h//2],
                "confidence": 0.8,
                "area": area,
                "aspect_ratio": aspect_ratio
            }
        
        # Room detection (large rectangular areas)
        if area > 10000 and 0.5 < aspect_ratio < 2.0:
            return {
                "type": "rooms",
                "bbox": [x, y, w, h],
                "center": [x + w//2, y + h//2],
                "confidence": 0.5,
                "area": area,
                "aspect_ratio": aspect_ratio
            }
        
        return None
    
    def _is_door_like(self, contour: np.ndarray, aspect_ratio: float) -> bool:
        """Check if contour looks like a door"""
        # Doors are typically rectangular and near the bottom
        x, y, w, h = cv2.boundingRect(contour)
        image_height = 600  # Assuming typical image height
        
        # Door characteristics
        is_rectangular = 0.2 < aspect_ratio < 5.0
        is_near_bottom = y + h > image_height * 0.6  # In bottom 40% of image
        has_reasonable_size = 100 < w * h < 10000
        
        return is_rectangular and is_near_bottom and has_reasonable_size
    
    def _is_window_like(self, contour: np.ndarray, aspect_ratio: float) -> bool:
        """Check if contour looks like a window"""
        # Windows are typically square-ish and higher up
        x, y, w, h = cv2.boundingRect(contour)
        image_height = 600  # Assuming typical image height
        
        # Window characteristics
        is_squareish = 0.5 < aspect_ratio < 2.0
        is_higher_up = y < image_height * 0.8  # In top 80% of image
        has_reasonable_size = 50 < w * h < 5000
        
        return is_squareish and is_higher_up and has_reasonable_size
    
    def _sam_architectural_detection(self, image_rgb: np.ndarray, cv_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Use SAM to refine architectural element detection"""
        if self.predictor is None:
            return []
        
        # Set image for SAM
        self.predictor.set_image(image_rgb)
        
        sam_results = []
        
        # Use CV results as input points for SAM
        for element_type, elements in cv_results.items():
            for element in elements:
                center_x, center_y = element["center"]
                
                # Get SAM prediction for this point
                masks, scores, logits = self.predictor.predict(
                    point_coords=np.array([[center_x, center_y]]),
                    point_labels=np.array([1]),  # Positive point
                    multimask_output=True
                )
                
                # Get best mask
                best_mask_idx = np.argmax(scores)
                mask = masks[best_mask_idx]
                score = scores[best_mask_idx]
                
                if score > 0.5:  # Good confidence
                    # Find bounding box from mask
                    y_indices, x_indices = np.where(mask)
                    if len(y_indices) > 0 and len(x_indices) > 0:
                        x_min, x_max = x_indices.min(), x_indices.max()
                        y_min, y_max = y_indices.min(), y_indices.max()
                        
                        sam_result = {
                            "type": element_type,
                            "bbox": [x_min, y_min, x_max - x_min, y_max - y_min],
                            "center": [center_x, center_y],
                            "confidence": float(score),
                            "mask": mask,
                            "cv_confidence": element["confidence"]
                        }
                        sam_results.append(sam_result)
        
        return sam_results
    
    def _combine_detections(self, cv_results: Dict[str, Any], sam_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Combine CV and SAM detections for better results"""
        combined = {
            "total_elements": 0,
            "element_types": {},
            "high_confidence_elements": [],
            "analysis_summary": {}
        }
        
        # Count CV detections
        for element_type, elements in cv_results.items():
            combined["element_types"][element_type] = len(elements)
            combined["total_elements"] += len(elements)
            
            # Add high confidence elements
            for element in elements:
                if element["confidence"] > 0.6:
                    combined["high_confidence_elements"].append(element)
        
        # Add SAM refinements
        for sam_element in sam_results:
            if sam_element["confidence"] > 0.7:
                combined["high_confidence_elements"].append(sam_element)
        
        # Create analysis summary
        combined["analysis_summary"] = {
            "doors_detected": len(cv_results.get("doors", [])),
            "windows_detected": len(cv_results.get("windows", [])),
            "walls_detected": len(cv_results.get("walls", [])),
            "rooms_detected": len(cv_results.get("rooms", [])),
            "sam_refinements": len(sam_results),
            "overall_confidence": len(combined["high_confidence_elements"]) / max(combined["total_elements"], 1)
        }
        
        return combined
    
    def create_annotated_image(self, image_path: str, results: Dict[str, Any], output_path: str):
        """Create annotated image showing detections"""
        image = cv2.imread(image_path)
        if image is None:
            return
        
        # Draw CV detections
        colors = {
            "doors": (0, 0, 255),      # Red
            "windows": (0, 255, 0),    # Green
            "walls": (255, 0, 0),      # Blue
            "rooms": (255, 255, 0)     # Yellow
        }
        
        # Draw CV results
        for element_type, elements in results["cv_detections"].items():
            color = colors.get(element_type, (128, 128, 128))
            for element in elements:
                x, y, w, h = element["bbox"]
                cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)
                cv2.putText(image, f"{element_type}: {element['confidence']:.2f}", 
                           (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        
        # Draw SAM results
        for sam_element in results["sam_detections"]:
            if sam_element["confidence"] > 0.7:
                x, y, w, h = sam_element["bbox"]
                cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 255), 3)  # Magenta for SAM
                cv2.putText(image, f"SAM: {sam_element['type']}", 
                           (x, y - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 1)
        
        # Save annotated image
        cv2.imwrite(output_path, image)
        print(f"✓ Annotated image saved to: {output_path}")

def main():
    """Main function"""
    analyzer = SAMEnhancedArchitecturalAnalyzer()
    
    # Test with sample images
    test_images = ["data/sample_plan.jpg", "data/sample_elevation.jpg"]
    
    for image_path in test_images:
        if Path(image_path).exists():
            print(f"\n{'='*60}")
            results = analyzer.detect_architectural_elements_with_sam(image_path)
            
            # Create annotated image
            output_path = f"output/sam_enhanced_{Path(image_path).stem}.jpg"
            analyzer.create_annotated_image(image_path, results, output_path)
            
            # Print results
            print(f"📊 Results for {Path(image_path).name}:")
            print(f"   Total elements: {results['combined_analysis']['total_elements']}")
            print(f"   High confidence: {len(results['combined_analysis']['high_confidence_elements'])}")
            print(f"   SAM refinements: {results['combined_analysis']['analysis_summary']['sam_refinements']}")

if __name__ == "__main__":
    main()
'''
    
    # Save the enhanced pipeline
    with open("scripts/sam_enhanced_architectural_analysis.py", 'w', encoding='utf-8') as f:
        f.write(enhanced_script)
    
    print(f"✓ Enhanced SAM pipeline created: scripts/sam_enhanced_architectural_analysis.py")
    
    return True

if __name__ == "__main__":
    analyze_reco_dataset()
    analyze_sample_images()
    create_sam_enhanced_pipeline() 