#!/usr/bin/env python3
"""
SAM2 Segmentation Module (Fixed)
Uses the original SAM models which are compatible with transformers
"""

import cv2
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
import torch
import os

# SAM imports via Hugging Face (using original SAM models)
try:
    from transformers import SamModel, SamProcessor
    SAM_AVAILABLE = True
except ImportError:
    SAM_AVAILABLE = False
    print("⚠️ SAM not available. Install transformers package.")

class SAM2Segmenter:
    """SAM2 segmenter using original SAM models for compatibility"""
    
    def __init__(self, model_name: str = "facebook/sam-vit-base"):
        """
        Initialize SAM2 segmenter with original SAM models
        
        Args:
            model_name (str): Hugging Face model name for SAM
        """
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = None
        self.processor = None
        
        # Load SAM model
        if SAM_AVAILABLE:
            self._load_sam_model()
        else:
            print("❌ SAM not available - install transformers package")
    
    def _load_sam_model(self):
        """Load SAM model from Hugging Face"""
        try:
            print(f"✓ Loading SAM model: {self.model_name}")
            print(f"Using device: {self.device}")
            
            self.processor = SamProcessor.from_pretrained(self.model_name)
            self.model = SamModel.from_pretrained(self.model_name).to(self.device)
            
            print("✓ SAM model loaded successfully")
            
        except Exception as e:
            print(f"❌ Error loading SAM model: {e}")
            print("💡 Available models: facebook/sam-vit-base, facebook/sam-vit-large, facebook/sam-vit-huge")
            self.model = None
            self.processor = None
    
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
        if self.model is None or self.processor is None:
            return {"error": "SAM model not loaded", "segments": []}
        
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                return {"error": "Could not load image", "segments": []}
            
            # Convert to RGB for SAM
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            segments = []
            
            # Process point prompts
            if points:
                for i, point in enumerate(points):
                    try:
                        # Prepare inputs for SAM
                        inputs = self.processor(
                            image_rgb, 
                            input_points=[[[point[0], point[1]]]], 
                            return_tensors="pt"
                        ).to(self.device)
                        
                        # Predict mask
                        with torch.no_grad():
                            outputs = self.model(**inputs)
                        
                        # Post-process masks
                        masks = self.processor.image_processor.post_process_masks(
                            outputs.pred_masks.cpu(),
                            inputs["original_sizes"].cpu(),
                            inputs["reshaped_input_sizes"].cpu()
                        )
                        
                        # Get the best mask
                        mask = masks[0][0].numpy()  # First image, first mask
                        score = outputs.iou_scores[0][0].item()
                        
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
                        # Debug: Print box format
                        print(f"Processing box {i}: {box} (type: {type(box)})")
                        
                        # Ensure box is in correct format for SAM
                        # DINO returns [x1, y1, x2, y2], SAM expects different formats depending on version
                        if isinstance(box, list) and len(box) == 4:
                            # Try multiple box formats to see which works
                            x1, y1, x2, y2 = box
                            
                            # Method 1: Try the format that should work according to docs
                            try:
                                inputs = self.processor(
                                    image_rgb, 
                                    input_boxes=[[[float(x1), float(y1), float(x2), float(y2)]]], 
                                    return_tensors="pt"
                                ).to(self.device)
                                print(f"✓ Method 1 worked for box {i}")
                            except Exception as e1:
                                print(f"Method 1 failed: {e1}")
                                
                                # Method 2: Try without triple nesting
                                try:
                                    inputs = self.processor(
                                        image_rgb, 
                                        input_boxes=[[float(x1), float(y1), float(x2), float(y2)]], 
                                        return_tensors="pt"
                                    ).to(self.device)
                                    print(f"✓ Method 2 worked for box {i}")
                                except Exception as e2:
                                    print(f"Method 2 failed: {e2}")
                                    
                                    # Method 3: Try single box format
                                    try:
                                        inputs = self.processor(
                                            image_rgb, 
                                            input_boxes=[float(x1), float(y1), float(x2), float(y2)], 
                                            return_tensors="pt"
                                        ).to(self.device)
                                        print(f"✓ Method 3 worked for box {i}")
                                    except Exception as e3:
                                        print(f"Method 3 failed: {e3}")
                                        print(f"All methods failed for box {i}, skipping...")
                                        continue
                        else:
                            print(f"Invalid box format: {box}")
                            continue
                        
                        # Predict mask
                        with torch.no_grad():
                            outputs = self.model(**inputs)
                        
                        # Post-process masks
                        masks = self.processor.image_processor.post_process_masks(
                            outputs.pred_masks.cpu(),
                            inputs["original_sizes"].cpu(),
                            inputs["reshaped_input_sizes"].cpu()
                        )
                        
                        # Get the best mask
                        mask = masks[0][0].numpy()  # First image, first mask
                        
                        # Handle IoU scores - SAM outputs multiple scores, take the maximum
                        try:
                            iou_scores = outputs.iou_scores[0][0]  # Shape: [3] typically
                            print(f"IoU scores shape: {iou_scores.shape}, values: {iou_scores}")
                            
                            if iou_scores.numel() > 1:
                                # Multiple scores - take the maximum
                                score = iou_scores.max().item()
                                print(f"Multiple IoU scores: {iou_scores.tolist()}, using max: {score:.3f}")
                            else:
                                # Single score
                                score = iou_scores.item()
                                print(f"Single IoU score: {score:.3f}")
                        except Exception as score_error:
                            print(f"Error extracting IoU score: {score_error}")
                            print(f"IoU scores tensor: {outputs.iou_scores}")
                            print(f"IoU scores shape: {outputs.iou_scores.shape}")
                            # Fallback to a default score
                            score = 0.5
                            print(f"Using fallback score: {score}")
                        
                        segments.append({
                            "type": "box_prompt",
                            "prompt_id": i,
                            "box": box,
                            "mask": mask,
                            "confidence": float(score),
                            "area": np.sum(mask)
                        })
                        
                        print(f"✓ Successfully processed box {i} with confidence {score:.3f}")
                        
                    except Exception as e:
                        print(f"Error processing box {i}: {e}")
                        import traceback
                        traceback.print_exc()
            
            return {
                "segments": segments,
                "total_segments": len(segments),
                "image_shape": image.shape,
                "model_name": self.model_name
            }
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {"error": f"Segmentation failed: {e}", "segments": []}
    
    def auto_segment(self, image_path: str, points_per_side: int = 32) -> Dict[str, Any]:
        """
        Automatically segment image using grid points
        
        Args:
            image_path (str): Path to input image
            points_per_side (int): Number of points per side for grid generation
            
        Returns:
            dict: Auto-segmentation results
        """
        if self.model is None or self.processor is None:
            return {"error": "SAM model not loaded", "segments": []}
        
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                return {"error": "Could not load image", "segments": []}
            
            # Convert to RGB
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            height, width = image.shape[:2]
            
            # Generate grid points
            points = []
            step = min(width, height) // points_per_side
            
            for y in range(step // 2, height, step):
                for x in range(step // 2, width, step):
                    points.append((x, y))
            
            # Limit number of points to avoid memory issues
            if len(points) > 500:  # Reduced from 1000 for better performance
                points = points[::len(points)//500]
            
            # Segment using points
            return self.segment_image(image_path, points=points)
            
        except Exception as e:
            return {"error": f"Auto-segmentation failed: {e}", "segments": []}
    
    def segment_everything(self, image_path: str) -> Dict[str, Any]:
        """
        Segment everything in the image using automatic mask generation
        
        Args:
            image_path (str): Path to input image
            
        Returns:
            dict: Complete segmentation results
        """
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                return {"error": "Could not load image", "segments": []}
            
            # Convert to RGB
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Try using transformers pipeline for automatic mask generation
            try:
                from transformers import pipeline
                
                mask_generator = pipeline(
                    "mask-generation",
                    model=self.model_name,
                    device=0 if self.device == "cuda" else -1,
                    points_per_batch=32  # Reduced for stability
                )
                
                # Generate all masks
                outputs = mask_generator(image_rgb, points_per_batch=32)
                
                # Convert to our format
                segments = []
                for i, mask_data in enumerate(outputs["masks"]):
                    segments.append({
                        "type": "auto_mask",
                        "prompt_id": i,
                        "mask": mask_data,
                        "confidence": 1.0,  # Pipeline doesn't return confidence
                        "area": np.sum(mask_data),
                        "stability_score": outputs.get("stability_scores", [1.0])[i] if i < len(outputs.get("stability_scores", [])) else 1.0
                    })
                
                return {
                    "segments": segments,
                    "total_segments": len(segments),
                    "image_shape": image.shape,
                    "model_name": self.model_name,
                    "method": "automatic_mask_generation"
                }
                
            except Exception as e:
                print(f"Pipeline method failed: {e}")
                # Fallback to grid-based segmentation
                return self.auto_segment(image_path, points_per_side=16)
            
        except Exception as e:
            print(f"Error in segment_everything: {e}")
            # Final fallback to grid-based segmentation
            return self.auto_segment(image_path, points_per_side=12)
    
    def segment_with_boxes(self, image_path: str, boxes: List[List[int]], 
                          labels: Optional[List[str]] = None) -> List[Dict]:
        """
        Segment image using bounding box prompts
        
        Args:
            image_path (str): Path to input image
            boxes (List[List[int]]): List of bounding boxes [[x1, y1, x2, y2], ...]
            labels (Optional[List[str]]): Optional labels for each box
            
        Returns:
            List[Dict]: List of segmentation results
        """
        try:
            # Use the existing segment_image method with boxes
            result = self.segment_image(image_path=image_path, boxes=boxes)
            
            segments = result.get("segments", [])
            
            # Add labels if provided
            if labels and len(labels) == len(segments):
                for i, segment in enumerate(segments):
                    segment["label"] = labels[i]
            
            return segments
            
        except Exception as e:
            print(f"❌ Error in segment_with_boxes: {e}")
            return []
    
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
        by_type = {}
        total_area = 0
        confidences = []
        
        for segment in segments:
            seg_type = segment.get("type", "unknown")
            by_type[seg_type] = by_type.get(seg_type, 0) + 1
            total_area += segment.get("area", 0)
            if "confidence" in segment:
                confidences.append(segment["confidence"])
        
        summary = {
            "total": len(segments),
            "by_type": by_type,
            "total_area": total_area,
            "average_area": total_area / len(segments) if segments else 0
        }
        
        if confidences:
            summary["confidence_stats"] = {
                "mean": np.mean(confidences),
                "std": np.std(confidences),
                "min": np.min(confidences),
                "max": np.max(confidences)
            }
        
        return summary
    
    def visualize_segments(self, image_path: str, segments: List[Dict], 
                          output_path: str, show_masks: bool = True, 
                          show_points: bool = True) -> bool:
        """
        Visualize segmentation results
        
        Args:
            image_path (str): Path to input image
            segments (list): List of segment dictionaries
            output_path (str): Path to save visualization
            show_masks (bool): Whether to show mask overlays
            show_points (bool): Whether to show prompt points
            
        Returns:
            bool: Success status
        """
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                return False
            
            # Create overlay
            overlay = image.copy()
            
            # Colors for different segments
            colors = [
                (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0),
                (255, 0, 255), (0, 255, 255), (128, 0, 128), (255, 165, 0)
            ]
            
            for i, segment in enumerate(segments):
                color = colors[i % len(colors)]
                
                # Draw mask
                if show_masks and "mask" in segment:
                    mask = segment["mask"]
                    if mask.dtype != np.uint8:
                        mask = (mask * 255).astype(np.uint8)
                    
                    # Create colored mask
                    colored_mask = np.zeros_like(image)
                    colored_mask[mask > 0] = color
                    
                    # Blend with image
                    overlay = cv2.addWeighted(overlay, 0.7, colored_mask, 0.3, 0)
                
                # Draw points
                if show_points and "point" in segment:
                    point = segment["point"]
                    cv2.circle(overlay, point, 5, color, -1)
                    cv2.circle(overlay, point, 7, (255, 255, 255), 2)
                
                # Draw boxes
                if "box" in segment:
                    box = segment["box"]
                    if len(box) == 4:
                        x1, y1, w, h = box
                        cv2.rectangle(overlay, (x1, y1), (x1 + w, y1 + h), color, 2)
            
            # Save result
            cv2.imwrite(output_path, overlay)
            print(f"✓ Visualization saved to: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error creating visualization: {e}")
            return False

# Convenience function for backward compatibility
def create_sam2_segmenter(model_name: str = "facebook/sam-vit-base") -> SAM2Segmenter:
    """Create a SAM2Segmenter instance"""
    return SAM2Segmenter(model_name=model_name)

if __name__ == "__main__":
    # Test the SAM2 module
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python sam2_module_fixed.py <image_path>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    # Test SAM2 with different model sizes
    models_to_test = [
        "facebook/sam-vit-base",
        # "facebook/sam-vit-large",  # Uncomment if you have more memory
        # "facebook/sam-vit-huge"    # Uncomment if you have lots of memory
    ]
    
    for model_name in models_to_test:
        print(f"\n{'='*60}")
        print(f"Testing {model_name}")
        print('='*60)
        
        # Test SAM2
        sam2 = SAM2Segmenter(model_name=model_name)
        
        if sam2.model is not None:
            print(f"Testing SAM2 on: {image_path}")
            
            # Test auto-segmentation
            results = sam2.segment_everything(image_path)
            
            if "error" not in results:
                print(f"✓ Generated {results['total_segments']} segments")
                
                # Get summary
                summary = sam2.get_segmentation_summary(results["segments"])
                print(f"Summary: {summary}")
                
                # Create visualization
                model_short = model_name.split('/')[-1]
                output_path = f"sam2_visualization_{model_short}_{Path(image_path).stem}.jpg"
                sam2.visualize_segments(image_path, results["segments"], output_path)
            else:
                print(f"❌ Error: {results['error']}")
        else:
            print("❌ SAM2 model not loaded") 