#!/usr/bin/env python3
"""
YOLO Object Detection Module
Detects buildings, structures, and other elements in site plans using YOLOv8
"""

import os
import cv2
import numpy as np
from ultralytics import YOLO
from typing import Dict, Any, List, Tuple
import json

# Set up E drive environment before importing ultralytics
from utils.e_drive_setup import setup_e_drive_environment
setup_e_drive_environment()

class YOLODetector:
    def __init__(self, model_path: str = "yolov8n.pt", confidence_threshold: float = 0.5):
        """
        Initialize YOLO detector
        
        Args:
            model_path (str): Path to YOLO model file
            confidence_threshold (float): Minimum confidence for detections
        """
        self.confidence_threshold = confidence_threshold
        self.model = None
        self._load_model(model_path)
    
    def _load_model(self, model_path: str):
        """Load YOLO model with E drive cache configuration"""
        try:
            print(f"Loading YOLO model: {model_path}")
            
            # Set ultralytics cache directory to E drive
            e_cache_dir = setup_e_drive_environment()
            ultralytics_cache = os.path.join(e_cache_dir, "ultralytics")
            os.environ['ULTRAALYTICS_CACHE_DIR'] = ultralytics_cache
            
            # Load model
            self.model = YOLO(model_path)
            print("✓ YOLO model loaded successfully")
            
        except Exception as e:
            print(f"Error loading YOLO model: {e}")
            raise
    
    def detect_elements(self, image_path: str) -> List[Dict[str, Any]]:
        """
        Detect elements in an image
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            List[Dict]: List of detections with bounding boxes and confidence scores
        """
        if self.model is None:
            raise ValueError("Model not loaded")
        
        try:
            # Run detection
            results = self.model(image_path, conf=self.confidence_threshold)
            
            detections = []
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        # Get coordinates
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        
                        # Get confidence and class
                        confidence = float(box.conf[0].cpu().numpy())
                        class_id = int(box.cls[0].cpu().numpy())
                        class_name = result.names[class_id]
                        
                        detection = {
                            "bbox": [float(x1), float(y1), float(x2), float(y2)],
                            "confidence": confidence,
                            "class_id": class_id,
                            "class_name": class_name
                        }
                        detections.append(detection)
            
            return detections
            
        except Exception as e:
            print(f"Error during detection: {e}")
            return []
    
    def analyze_site_plan_elements(self, image_path: str, confidence_threshold: float = None) -> Dict[str, Any]:
        """
        Analyze site plan for architectural elements
        
        Args:
            image_path (str): Path to the site plan image
            confidence_threshold (float): Optional confidence threshold override
            
        Returns:
            dict: Analysis results with detections and summary
        """
        if confidence_threshold is not None:
            self.confidence_threshold = confidence_threshold
        
        print(f"Analyzing site plan: {image_path}")
        print(f"Confidence threshold: {self.confidence_threshold}")
        
        # Perform detection
        detections = self.detect_elements(image_path)
        
        # Create summary
        summary = self._create_detection_summary(detections)
        
        results = {
            "image_path": image_path,
            "confidence_threshold": self.confidence_threshold,
            "detections": detections,
            "summary": summary
        }
        
        return results
    
    def _create_detection_summary(self, detections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create a summary of detections
        
        Args:
            detections (List[Dict]): List of detection results
            
        Returns:
            dict: Summary statistics
        """
        if not detections:
            return {
                "total_detections": 0,
                "high_confidence_detections": 0,
                "detection_summary": {},
                "average_confidence": 0.0
            }
        
        # Count detections by class
        class_counts = {}
        high_confidence_detections = []
        total_confidence = 0.0
        
        for detection in detections:
            class_name = detection["class_name"]
            confidence = detection["confidence"]
            
            # Count by class
            class_counts[class_name] = class_counts.get(class_name, 0) + 1
            
            # Track high confidence detections
            if confidence >= self.confidence_threshold:
                high_confidence_detections.append(detection)
            
            total_confidence += confidence
        
        summary = {
            "total_detections": len(detections),
            "high_confidence_detections": len(high_confidence_detections),
            "detection_summary": class_counts,
            "average_confidence": total_confidence / len(detections) if detections else 0.0
        }
        
        return summary


# Global detector instance
yolo_detector = YOLODetector()

def analyze_site_plan_elements(image_path: str, confidence_threshold: float = 0.5) -> Dict[str, Any]:
    """
    Convenience function for site plan analysis
    
    Args:
        image_path (str): Path to the site plan image
        confidence_threshold (float): Minimum confidence for detections
        
    Returns:
        dict: Analysis results
    """
    return yolo_detector.analyze_site_plan_elements(image_path, confidence_threshold)

def draw_detections_on_image(image_path: str, detection_results: Dict[str, Any], output_path: str) -> str:
    """
    Draw detection bounding boxes on image
    
    Args:
        image_path (str): Path to input image
        detection_results (dict): Results from analyze_site_plan_elements
        output_path (str): Path to save annotated image
        
    Returns:
        str: Path to saved annotated image
    """
    try:
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not load image: {image_path}")
        
        # Draw detections
        detections = detection_results.get("detections", [])
        
        for detection in detections:
            bbox = detection["bbox"]
            confidence = detection["confidence"]
            class_name = detection["class_name"]
            
            # Convert coordinates to integers
            x1, y1, x2, y2 = map(int, bbox)
            
            # Draw bounding box
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Draw label
            label = f"{class_name}: {confidence:.2f}"
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
            
            # Draw label background
            cv2.rectangle(image, (x1, y1 - label_size[1] - 10), (x1 + label_size[0], y1), (0, 255, 0), -1)
            
            # Draw label text
            cv2.putText(image, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        
        # Save annotated image
        cv2.imwrite(output_path, image)
        print(f"✓ Annotated image saved to: {output_path}")
        
        return output_path
        
    except Exception as e:
        print(f"Error drawing detections: {e}")
        return ""

def get_detection_statistics(detection_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get detailed statistics from detection results
    
    Args:
        detection_results (dict): Results from analyze_site_plan_elements
        
    Returns:
        dict: Detailed statistics
    """
    detections = detection_results.get("detections", [])
    summary = detection_results.get("summary", {})
    
    if not detections:
        return {
            "total_elements": 0,
            "element_types": {},
            "confidence_distribution": {},
            "spatial_distribution": {}
        }
    
    # Analyze confidence distribution
    confidence_ranges = {
        "high": 0,    # 0.8-1.0
        "medium": 0,  # 0.5-0.8
        "low": 0      # 0.0-0.5
    }
    
    for detection in detections:
        conf = detection["confidence"]
        if conf >= 0.8:
            confidence_ranges["high"] += 1
        elif conf >= 0.5:
            confidence_ranges["medium"] += 1
        else:
            confidence_ranges["low"] += 1
    
    # Analyze spatial distribution (simple quadrant analysis)
    image_width = 1000  # Assume standard width for analysis
    image_height = 1000  # Assume standard height for analysis
    
    quadrants = {"top_left": 0, "top_right": 0, "bottom_left": 0, "bottom_right": 0}
    
    for detection in detections:
        bbox = detection["bbox"]
        center_x = (bbox[0] + bbox[2]) / 2
        center_y = (bbox[1] + bbox[3]) / 2
        
        # Determine quadrant
        if center_x < image_width / 2:
            if center_y < image_height / 2:
                quadrants["top_left"] += 1
            else:
                quadrants["bottom_left"] += 1
        else:
            if center_y < image_height / 2:
                quadrants["top_right"] += 1
            else:
                quadrants["bottom_right"] += 1
    
    statistics = {
        "total_elements": len(detections),
        "element_types": summary.get("detection_summary", {}),
        "confidence_distribution": confidence_ranges,
        "spatial_distribution": quadrants,
        "average_confidence": summary.get("average_confidence", 0.0)
    }
    
    return statistics
