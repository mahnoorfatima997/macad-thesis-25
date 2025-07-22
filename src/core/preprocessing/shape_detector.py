#!/usr/bin/env python3
"""
OpenCV Shape Detection Module
Based on PyImageSearch tutorial for detecting geometric shapes in site plans
"""

import cv2
import numpy as np
import os
from typing import Dict, Any, List, Tuple
from PIL import Image
import json
import tempfile

class ShapeDetector:
    """
    Shape detector class based on PyImageSearch tutorial
    Detects and classifies geometric shapes in site plans
    """
    
    def __init__(self):
        """Initialize the shape detector"""
        pass
    
    def detect(self, contour):
        """
        Detect the shape of a contour based on vertex count
        
        Args:
            contour: OpenCV contour
            
        Returns:
            str: Shape name (triangle, square, rectangle, pentagon, circle, etc.)
        """
        # Initialize the shape name and approximate the contour
        shape = "unidentified"
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.04 * peri, True)
        
        # If the shape is a triangle, it will have 3 vertices
        if len(approx) == 3:
            shape = "triangle"
        
        # If the shape has 4 vertices, it is either a square or a rectangle
        elif len(approx) == 4:
            # Compute the bounding box of the contour and use the
            # bounding box to compute the aspect ratio
            (x, y, w, h) = cv2.boundingRect(approx)
            ar = w / float(h)
            
            # A square will have an aspect ratio that is approximately
            # equal to one, otherwise, the shape is a rectangle
            shape = "square" if ar >= 0.95 and ar <= 1.05 else "rectangle"
        
        # If the shape is a pentagon, it will have 5 vertices
        elif len(approx) == 5:
            shape = "pentagon"
        
        # If the shape is a hexagon, it will have 6 vertices
        elif len(approx) == 6:
            shape = "hexagon"
        
        # If the shape is an octagon, it will have 8 vertices
        elif len(approx) == 8:
            shape = "octagon"
        
        # Otherwise, we assume the shape is a circle
        else:
            shape = "circle"
        
        return shape

class SitePlanShapeAnalyzer:
    """
    Comprehensive shape analysis for site plans
    Combines shape detection with site-specific analysis
    """
    
    def __init__(self):
        """Initialize the shape analyzer"""
        self.shape_detector = ShapeDetector()
        
        # Use standard temp directory
        self.temp_dir = tempfile.mkdtemp(prefix="shape_analysis_")
    
    def preprocess_image_for_shape_detection(self, image_path: str) -> Tuple[np.ndarray, float]:
        """
        Preprocess image for optimal shape detection
        
        Args:
            image_path (str): Path to the input image
            
        Returns:
            tuple: (preprocessed_image, scale_ratio)
        """
        # Load the image and resize it to a smaller factor so that
        # the shapes can be approximated better
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not load image: {image_path}")
        
        # Resize for better shape approximation
        resized = cv2.resize(image, (800, 600))
        ratio = image.shape[0] / float(resized.shape[0])
        
        # Convert the resized image to grayscale, blur it slightly,
        # and threshold it
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Use adaptive thresholding for better results
        thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        return thresh, ratio
    
    def detect_shapes(self, image_path: str, min_area: int = 100) -> Dict[str, Any]:
        """
        Detect all shapes in the site plan image
        
        Args:
            image_path (str): Path to the site plan image
            min_area (int): Minimum contour area to consider
            
        Returns:
            dict: Shape detection results
        """
        try:
            # Preprocess image
            thresh, ratio = self.preprocess_image_for_shape_detection(image_path)
            
            # Find contours in the thresholded image
            contours, _ = cv2.findContours(
                thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            
            # Initialize results
            shape_results = {
                "total_shapes": 0,
                "shapes_by_type": {},
                "shape_details": [],
                "processing_info": {
                    "image_path": image_path,
                    "scale_ratio": ratio,
                    "min_area": min_area
                }
            }
            
            # Process each contour
            for i, contour in enumerate(contours):
                # Filter by area
                area = cv2.contourArea(contour)
                if area < min_area:
                    continue
                
                # Detect shape
                shape = self.shape_detector.detect(contour)
                
                # Get bounding box and center
                (x, y, w, h) = cv2.boundingRect(contour)
                M = cv2.moments(contour)
                if M["m00"] != 0:
                    cX = int(M["m10"] / M["m00"])
                    cY = int(M["m01"] / M["m00"])
                else:
                    cX, cY = x + w//2, y + h//2
                
                # Store shape details
                shape_detail = {
                    "id": i,
                    "shape": shape,
                    "area": area,
                    "center": (cX, cY),
                    "bounding_box": (x, y, w, h),
                    "perimeter": cv2.arcLength(contour, True)
                }
                
                shape_results["shape_details"].append(shape_detail)
                
                # Update counts
                shape_results["total_shapes"] += 1
                shape_results["shapes_by_type"][shape] = shape_results["shapes_by_type"].get(shape, 0) + 1
            
            return shape_results
            
        except Exception as e:
            return {
                "error": f"Error in shape detection: {str(e)}",
                "total_shapes": 0,
                "shapes_by_type": {},
                "shape_details": []
            }
    
    def analyze_site_plan_structures(self, image_path: str) -> Dict[str, Any]:
        """
        Analyze site plan for architectural and structural elements
        
        Args:
            image_path (str): Path to the site plan image
            
        Returns:
            dict: Structural analysis results
        """
        shape_results = self.detect_shapes(image_path, min_area=50)
        
        if "error" in shape_results:
            return shape_results
        
        # Analyze structures based on detected shapes
        analysis = {
            "building_structures": [],
            "site_features": [],
            "circulation_elements": [],
            "structural_analysis": {}
        }
        
        for shape_detail in shape_results["shape_details"]:
            shape = shape_detail["shape"]
            area = shape_detail["area"]
            
            # Classify based on shape and size
            if shape in ["rectangle", "square"]:
                if area > 1000:  # Large rectangles likely buildings
                    analysis["building_structures"].append({
                        "type": "building",
                        "shape": shape,
                        "area": area,
                        "center": shape_detail["center"],
                        "dimensions": shape_detail["bounding_box"][2:]
                    })
                else:  # Smaller rectangles might be rooms or features
                    analysis["site_features"].append({
                        "type": "feature",
                        "shape": shape,
                        "area": area,
                        "center": shape_detail["center"]
                    })
            
            elif shape == "circle":
                # Circles might be roundabouts, trees, or decorative elements
                analysis["site_features"].append({
                    "type": "circular_feature",
                    "shape": shape,
                    "area": area,
                    "center": shape_detail["center"]
                })
            
            elif shape in ["triangle", "pentagon", "hexagon"]:
                # Irregular shapes might be circulation elements or special features
                analysis["circulation_elements"].append({
                    "type": "irregular_structure",
                    "shape": shape,
                    "area": area,
                    "center": shape_detail["center"]
                })
        
        # Add structural analysis summary
        analysis["structural_analysis"] = {
            "total_structures": len(analysis["building_structures"]),
            "total_features": len(analysis["site_features"]),
            "total_circulation": len(analysis["circulation_elements"]),
            "shape_distribution": shape_results["shapes_by_type"],
            "size_distribution": self._analyze_size_distribution(shape_results["shape_details"])
        }
        
        return analysis
    
    def _analyze_size_distribution(self, shape_details: List[Dict]) -> Dict[str, Any]:
        """
        Analyze the size distribution of detected shapes
        
        Args:
            shape_details (list): List of shape detail dictionaries
            
        Returns:
            dict: Size distribution analysis
        """
        areas = [detail["area"] for detail in shape_details]
        
        if not areas:
            return {"error": "No shapes detected"}
        
        return {
            "min_area": min(areas),
            "max_area": max(areas),
            "avg_area": sum(areas) / len(areas),
            "small_objects": len([a for a in areas if a < 500]),
            "medium_objects": len([a for a in areas if 500 <= a < 2000]),
            "large_objects": len([a for a in areas if a >= 2000])
        }
    
    def create_annotated_image(self, image_path: str, output_path: str) -> str:
        """
        Create an annotated image showing detected shapes
        
        Args:
            image_path (str): Path to input image
            output_path (str): Path to save annotated image
            
        Returns:
            str: Path to annotated image
        """
        try:
            # Load and resize image
            image = cv2.imread(image_path)
            resized = cv2.resize(image, (800, 600))
            
            # Detect shapes
            shape_results = self.detect_shapes(image_path, min_area=50)
            
            if "error" in shape_results:
                return f"Error: {shape_results['error']}"
            
            # Draw shapes on image
            for shape_detail in shape_results["shape_details"]:
                # Get contour for drawing
                thresh, _ = self.preprocess_image_for_shape_detection(image_path)
                contours, _ = cv2.findContours(
                    thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
                )
                
                if shape_detail["id"] < len(contours):
                    contour = contours[shape_detail["id"]]
                    
                    # Draw contour
                    cv2.drawContours(resized, [contour], -1, (0, 255, 0), 2)
                    
                    # Draw shape label
                    cX, cY = shape_detail["center"]
                    cv2.putText(
                        resized, shape_detail["shape"], (cX, cY),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2
                    )
            
            # Save annotated image
            cv2.imwrite(output_path, resized)
            return output_path
            
        except Exception as e:
            return f"Error creating annotated image: {str(e)}"

# Global analyzer instance
shape_analyzer = SitePlanShapeAnalyzer()

def detect_shapes_in_site_plan(image_path: str) -> Dict[str, Any]:
    """
    Convenience function for shape detection
    
    Args:
        image_path (str): Path to the site plan image
        
    Returns:
        dict: Shape detection results
    """
    return shape_analyzer.detect_shapes(image_path)

def analyze_site_plan_structures(image_path: str) -> Dict[str, Any]:
    """
    Convenience function for structural analysis
    
    Args:
        image_path (str): Path to the site plan image
        
    Returns:
        dict: Structural analysis results
    """
    return shape_analyzer.analyze_site_plan_structures(image_path) 