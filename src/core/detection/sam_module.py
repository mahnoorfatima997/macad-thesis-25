#!/usr/bin/env python3
"""
SAM Segmentation Module
Clean, focused SAM (Segment Anything Model) for architectural segmentation
"""

import cv2
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
import torch
import os

# SAM imports
try:
    from segment_anything import sam_model_registry, SamPredictor
    SAM_AVAILABLE = True
except ImportError:
    SAM_AVAILABLE = False
    print("⚠️ SAM not available. Install segment-anything package.")

class SAMSegmenter:
    """Clean SAM segmenter for architectural elements"""
    
    def __init__(self, checkpoint_path: str = "src/models/sam/sam_vit_h_4b8939.pth"):
        """
        Initialize SAM segmenter
        
        Args:
            checkpoint_path (str): Path to SAM checkpoint
        """
        self.checkpoint_path = Path(checkpoint_path)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.sam = None
        self.predictor = None
        
        # Load SAM model
        if SAM_AVAILABLE:
            self._load_sam_model()
        else:
            print("❌ SAM not available - install segment-anything package")
    
    def _load_sam_model(self):
        """Load SAM model"""
        try:
            if self.checkpoint_path.exists():
                print(f"✓ Loading SAM model from {self.checkpoint_path}")
                self.sam = sam_model_registry["vit_h"](checkpoint=str(self.checkpoint_path))
                self.sam.to(device=self.device)
                self.predictor = SamPredictor(self.sam)
                print("✓ SAM model loaded successfully")
            else:
                print(f"❌ SAM model not found at {self.checkpoint_path}")
                self.sam = None
                self.predictor = None
        except Exception as e:
            print(f"❌ Error loading SAM model: {e}")
            self.sam = None
            self.predictor = None
    
    def segment_image(self, image_path: str, points: Optional[List[Tuple[int, int]]] = None, 
                     boxes: Optional[List[List[int]]] = None) -> Dict[str, Any]:
        """
        Segment image using SAM
        
        Args:
            image_path (str): Path to input image
            points (list): List of point prompts [(x, y), ...]
            boxes (list): List of box prompts [[x1, y1, x2, y2], ...]
            
        Returns:
            dict: Segmentation results with masks and metadata
        """
        if self.predictor is None:
            return {"error": "SAM model not loaded", "segments": []}
        
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                return {"error": "Could not load image", "segments": []}
            
            # Convert to RGB for SAM
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Set image in predictor
            self.predictor.set_image(image_rgb)
            
            segments = []
            
            # Process point prompts
            if points:
                for i, point in enumerate(points):
                    try:
                        # Predict mask for point
                        masks, scores, logits = self.predictor.predict(
                            point_coords=np.array([point]),
                            point_labels=np.array([1]),  # Foreground point
                            multimask_output=True
                        )
                        
                        # Get best mask
                        best_mask_idx = np.argmax(scores)
                        mask = masks[best_mask_idx]
                        score = scores[best_mask_idx]
                        
                        segments.append({
                            "type": "point_prompt",
                            "prompt_id": i,
                            "point": point,
                            "mask": mask,
                            "confidence": float(score),
                            "area": np.sum(mask)
                        })
                    except Exception as e:
                        print(f"Error processing point {i}: {e}")
            
            # Process box prompts
            if boxes:
                for i, box in enumerate(boxes):
                    try:
                        # Predict mask for box
                        masks, scores, logits = self.predictor.predict(
                            box=np.array(box),
                            multimask_output=True
                        )
                        
                        # Get best mask
                        best_mask_idx = np.argmax(scores)
                        mask = masks[best_mask_idx]
                        score = scores[best_mask_idx]
                        
                        segments.append({
                            "type": "box_prompt",
                            "prompt_id": i,
                            "box": box,
                            "mask": mask,
                            "confidence": float(score),
                            "area": np.sum(mask)
                        })
                    except Exception as e:
                        print(f"Error processing box {i}: {e}")
            
            return {
                "segments": segments,
                "total_segments": len(segments),
                "image_shape": image.shape,
                "model_path": str(self.checkpoint_path)
            }
            
        except Exception as e:
            return {"error": f"Segmentation failed: {e}", "segments": []}
    
    def auto_segment(self, image_path: str, num_points: int = 10) -> Dict[str, Any]:
        """
        Automatically segment image using grid points
        
        Args:
            image_path (str): Path to input image
            num_points (int): Number of points to use for segmentation
            
        Returns:
            dict: Auto-segmentation results
        """
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                return {"error": "Could not load image", "segments": []}
            
            # Generate grid points
            height, width = image.shape[:2]
            points = []
            
            for i in range(num_points):
                for j in range(num_points):
                    x = int((i + 0.5) * width / num_points)
                    y = int((j + 0.5) * height / num_points)
                    points.append((x, y))
            
            # Segment using points
            return self.segment_image(image_path, points=points)
            
        except Exception as e:
            return {"error": f"Auto-segmentation failed: {e}", "segments": []}
    
    def get_segmentation_summary(self, segments: List[Dict]) -> Dict[str, Any]:
        """
        Generate summary of segmentation results
        
        Args:
            segments (list): List of segment dictionaries
            
        Returns:
            dict: Summary statistics
        """
        if not segments:
            return {"total": 0, "by_type": {}, "total_area": 0}
        
        # Count by type
        type_counts = {}
        total_area = 0
        
        for segment in segments:
            segment_type = segment["type"]
            area = segment["area"]
            
            type_counts[segment_type] = type_counts.get(segment_type, 0) + 1
            total_area += area
        
        return {
            "total": len(segments),
            "by_type": type_counts,
            "total_area": total_area,
            "average_area": total_area / len(segments) if segments else 0
        } 