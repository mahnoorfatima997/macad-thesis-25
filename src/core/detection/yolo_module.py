#!/usr/bin/env python3
"""
YOLO Detection Module
Clean, focused YOLO object detection for architectural elements
"""

import cv2
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Tuple
from ultralytics import YOLO
import os

class YOLODetector:
    """Clean YOLO detector for architectural elements"""
    
    def __init__(self, model_path: str = "plan_images_training/runs/detect/improved_architectural_yolo/weights/best.pt", confidence_threshold: float = 0.3):
        """
        Initialize YOLO detector
        
        Args:
            model_path (str): Path to YOLO model
            confidence_threshold (float): Minimum confidence for detections
        """
        self.model_path = Path(model_path)
        self.confidence_threshold = confidence_threshold
        self.model = None
        
        # Load model
        self._load_model()
        
    def _load_model(self):
        """Load YOLO model"""
        try:
            print(f"Loading YOLO model: {self.model_path}")
            self.model = YOLO(str(self.model_path))
            print("✓ YOLO model loaded successfully")
        except Exception as e:
            print(f"❌ Error loading YOLO model: {e}")
            self.model = None
    
    def detect(self, image_path: str) -> Dict[str, Any]:
        """
        Detect objects in image using YOLO
        
        Args:
            image_path (str): Path to input image
            
        Returns:
            dict: Detection results with bounding boxes, confidence scores, and class names
        """
        if self.model is None:
            return {"error": "YOLO model not loaded", "detections": []}
        
        try:
            # Run detection
            results = self.model(image_path, conf=self.confidence_threshold)
            
            # Extract detections
            detections = []
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        # Get coordinates
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        
                        # Get confidence and class
                        confidence = float(box.conf[0])
                        class_id = int(box.cls[0])
                        class_name = result.names[class_id]
                        
                        detection = {
                            "bbox": [int(x1), int(y1), int(x2), int(y2)],
                            "confidence": confidence,
                            "class_id": class_id,
                            "class_name": class_name,
                            "area": (x2 - x1) * (y2 - y1)
                        }
                        detections.append(detection)
            
            return {
                "detections": detections,
                "total_detections": len(detections),
                "model_path": str(self.model_path),
                "confidence_threshold": self.confidence_threshold
            }
            
        except Exception as e:
            return {"error": f"Detection failed: {e}", "detections": []}
    
    def get_detection_summary(self, detections: List[Dict]) -> Dict[str, Any]:
        """
        Generate summary of detections
        
        Args:
            detections (list): List of detection dictionaries
            
        Returns:
            dict: Summary statistics
        """
        if not detections:
            return {"total": 0, "by_class": {}, "high_confidence": 0}
        
        # Count by class
        class_counts = {}
        high_confidence_count = 0
        
        for detection in detections:
            class_name = detection["class_name"]
            confidence = detection["confidence"]
            
            class_counts[class_name] = class_counts.get(class_name, 0) + 1
            
            if confidence > 0.7:
                high_confidence_count += 1
        
        return {
            "total": len(detections),
            "by_class": class_counts,
            "high_confidence": high_confidence_count,
            "average_confidence": sum(d["confidence"] for d in detections) / len(detections)
        } 