#!/usr/bin/env python3
"""
GPT-SAM Analyzer for Thesis Agents
Integrates our simple GPT Vision + SAM pipeline into the thesis-agents architecture
"""

import cv2
import numpy as np
import os
import tempfile
import json
from datetime import datetime
import base64
import re
from typing import Dict, Any, List

# Import SAM2 module from our detection directory
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'core', 'detection'))
from sam2_module_fixed import SAM2Segmenter

# Import OpenAI for GPT Vision
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️ OpenAI not available. Install with: pip install openai")

class GPTSAMAnalyzer:
    """GPT Vision + SAM analyzer for architectural images"""
    
    def __init__(self, openai_api_key=None):
        """Initialize the GPT-SAM analyzer"""
        
        # Initialize OpenAI client
        api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if OPENAI_AVAILABLE and api_key:
            self.client = OpenAI(api_key=api_key)
            self.gpt_available = True
            print("✅ GPT Vision initialized")
        else:
            self.client = None
            self.gpt_available = False
            print("⚠️ GPT Vision not available")
        
        # Initialize SAM
        try:
            self.sam = SAM2Segmenter(model_name="facebook/sam-vit-base")
            print("✅ SAM initialized")
        except Exception as e:
            print(f"❌ SAM initialization failed: {e}")
            self.sam = None
    
    def encode_image(self, image_path: str) -> str:
        """Encode image to base64 for GPT Vision"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def analyze_with_coordinates(self, image_path: str) -> Dict[str, Any]:
        """Use GPT Vision to analyze image and get precise coordinates"""
        
        if not self.gpt_available:
            return {"error": "GPT Vision not available"}
        
        # Get image dimensions
        image = cv2.imread(image_path)
        height, width = image.shape[:2]
        
        base64_image = self.encode_image(image_path)
        
        # Prompt GPT Vision to provide coordinates
        prompt = f"""
        Analyze this architectural image ({width}x{height} pixels) and provide precise coordinates for segmentation.
        
        You are an expert architectural analyst. Identify all rooms, doors, windows, and architectural elements.
        
        For each element you identify, provide:
        1. Exact bounding box coordinates [x1, y1, x2, y2] in pixels
        2. Element type (room, door, window, wall, etc.)
        3. Description of what you see
        4. Confidence level (0.0-1.0)
        
        COORDINATE SYSTEM:
        - Origin (0,0) is top-left corner
        - X increases rightward (0 to {width})
        - Y increases downward (0 to {height})
        
        Return ONLY a valid JSON object with this structure:
        {{
            "image_dimensions": {{"width": {width}, "height": {height}}},
            "analysis_confidence": 0.9,
            "spatial_elements": [
                {{
                    "type": "room",
                    "label": "living_room",
                    "description": "Large rectangular living space in center",
                    "bounding_box": [120, 80, 450, 280],
                    "center_point": [285, 180],
                    "coordinate_confidence": 0.9,
                    "area_pixels": 92400,
                    "visual_evidence": "clearly defined by wall boundaries"
                }},
                {{
                    "type": "door",
                    "label": "main_entrance",
                    "description": "Entry door on south wall",
                    "bounding_box": [200, 340, 240, 380],
                    "center_point": [220, 360],
                    "coordinate_confidence": 0.85,
                    "visual_evidence": "break in wall line with door symbol"
                }}
            ],
            "spatial_narrative": "Detailed description of the layout and spatial relationships",
            "circulation_analysis": {{
                "primary_path": "foyer -> living_room -> kitchen",
                "secondary_paths": ["living_room -> bedrooms"],
                "bottlenecks": ["narrow hallway"]
            }},
            "design_insights": {{
                "strengths": ["open living area", "good natural light"],
                "issues": ["small bedrooms", "narrow circulation"],
                "suggestions": ["enlarge master bedroom", "widen hallway"]
            }}
        }}
        
        Be as precise as possible with coordinates. Ensure all coordinates are within the image bounds.
        IMPORTANT: Return ONLY the JSON object, no additional text.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=2000,
                temperature=0.1
            )
            
            content = response.choices[0].message.content.strip()
            print(f"🔍 GPT Vision response length: {len(content)} characters")
            
            # Try to extract JSON
            json_result = self._extract_json_from_response(content)
            if json_result:
                return json_result
            
            # If JSON extraction fails, create fallback response
            print("🔄 Creating fallback response from text...")
            return self._create_fallback_from_text(content, width, height)
                
        except Exception as e:
            print(f"❌ GPT Vision API error: {e}")
            return self._create_error_response(width, height, str(e))
    
    def _extract_json_from_response(self, content: str) -> Dict[str, Any]:
        """Extract JSON from GPT response using multiple strategies"""
        
        # Strategy 1: Direct JSON extraction with regex
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            try:
                json_result = json.loads(json_str)
                print("✅ JSON extracted successfully")
                return json_result
            except json.JSONDecodeError as e:
                print(f"❌ JSON parsing failed: {e}")
                # Try to fix common JSON issues
                try:
                    fixed_json = self._fix_common_json_issues(json_str)
                    json_result = json.loads(fixed_json)
                    print("✅ JSON fixed and parsed successfully")
                    return json_result
                except:
                    print("❌ Could not fix JSON automatically")
        
        # Strategy 2: Extract from code blocks
        code_block_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
        if code_block_match:
            json_str = code_block_match.group(1)
            try:
                json_result = json.loads(json_str)
                print("✅ JSON extracted from code block")
                return json_result
            except json.JSONDecodeError:
                print("❌ JSON in code block is invalid")
        
        return None
    
    def _fix_common_json_issues(self, json_str: str) -> str:
        """Fix common JSON formatting issues"""
        # Remove trailing commas before closing brackets/braces
        json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
        return json_str
    
    def _create_fallback_from_text(self, content: str, width: int, height: int) -> Dict[str, Any]:
        """Create fallback response from text content"""
        return {
            "image_dimensions": {"width": width, "height": height},
            "analysis_confidence": 0.6,
            "spatial_elements": [
                {
                    "type": "room",
                    "label": "general_space",
                    "description": "General architectural space",
                    "bounding_box": [0, 0, width, height],
                    "center_point": [width//2, height//2],
                    "coordinate_confidence": 0.5,
                    "area_pixels": width * height,
                    "visual_evidence": "fallback analysis"
                }
            ],
            "spatial_narrative": content[:500] + "..." if len(content) > 500 else content,
            "circulation_analysis": {
                "primary_path": "unknown",
                "secondary_paths": [],
                "bottlenecks": []
            },
            "design_insights": {
                "strengths": ["Layout detected"],
                "issues": ["Unable to provide detailed analysis"],
                "suggestions": ["Consider uploading a clearer image"]
            },
            "analysis_method": "text_fallback"
        }
    
    def _create_error_response(self, width: int, height: int, error_msg: str) -> Dict[str, Any]:
        """Create error response"""
        return {
            "image_dimensions": {"width": width, "height": height},
            "analysis_confidence": 0.3,
            "spatial_elements": [
                {
                    "type": "room",
                    "label": "error_space",
                    "description": "Error in analysis",
                    "bounding_box": [0, 0, width, height],
                    "center_point": [width//2, height//2],
                    "coordinate_confidence": 0.3,
                    "area_pixels": width * height,
                    "visual_evidence": "error analysis"
                }
            ],
            "spatial_narrative": f"Error in analysis: {error_msg}",
            "circulation_analysis": {
                "primary_path": "unknown",
                "secondary_paths": [],
                "bottlenecks": []
            },
            "design_insights": {
                "strengths": [],
                "issues": [f"Analysis failed: {error_msg}"],
                "suggestions": ["Check your API key and try again"]
            },
            "analysis_method": "error_fallback"
        }
    
    def segment_with_sam(self, image_path: str, gpt_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Use SAM to segment based on GPT Vision coordinates"""
        
        if not self.sam:
            return {"error": "SAM not available"}
        
        spatial_elements = gpt_analysis.get("spatial_elements", [])
        
        if not spatial_elements:
            return {"error": "No spatial elements to segment"}
        
        # Extract bounding boxes from GPT analysis
        boxes = []
        labels = []
        
        for element in spatial_elements:
            bbox = element.get("bounding_box", [])
            label = element.get("label", "")
            confidence = element.get("coordinate_confidence", 0)
            
            if len(bbox) == 4 and confidence > 0.3:  # Filter low confidence detections
                boxes.append(bbox)
                labels.append(label)
        
        if not boxes:
            return {"error": "No valid bounding boxes for segmentation"}
        
        print(f"🎨 Creating SAM segments for {len(boxes)} elements")
        
        # Run SAM segmentation
        try:
            segmentation_results = self.sam.segment_image(image_path, boxes=boxes)
            return {
                "segments": segmentation_results.get("segments", []),
                "num_segments": len(boxes),
                "detection_labels": labels,
                "gpt_analysis": gpt_analysis
            }
        except Exception as e:
            print(f"❌ SAM segmentation error: {e}")
            return {"error": f"SAM segmentation failed: {e}"}
    
    def create_visualization(self, image_path: str, gpt_analysis: Dict[str, Any], sam_results: Dict[str, Any]) -> np.ndarray:
        """Create visualization of GPT analysis and SAM segmentation"""
        
        # Load the original image
        image = cv2.imread(image_path)
        if image is None:
            print("❌ Could not load image for visualization")
            return None
        
        # Create a copy for visualization
        viz_image = image.copy()
        height, width = viz_image.shape[:2]
        
        # Colors for different element types
        colors = {
            "room": (0, 255, 0),      # Green
            "door": (255, 0, 0),      # Red
            "window": (0, 0, 255),    # Blue
            "wall": (255, 255, 0),    # Cyan
            "kitchen": (255, 0, 255), # Magenta
            "bathroom": (0, 255, 255), # Yellow
            "bedroom": (128, 0, 128),  # Purple
            "living_room": (0, 128, 0), # Dark Green
            "dining_room": (128, 128, 0), # Olive
            "default": (255, 255, 255)  # White
        }
        
        # Draw GPT Vision spatial elements
        spatial_elements = gpt_analysis.get("spatial_elements", [])
        for element in spatial_elements:
            element_type = element.get("type", "default")
            bbox = element.get("bounding_box", [])
            label = element.get("label", "")
            confidence = element.get("coordinate_confidence", 0)
            
            if len(bbox) == 4:
                x1, y1, x2, y2 = map(int, bbox)
                color = colors.get(element_type, colors["default"])
                
                # Draw bounding box
                cv2.rectangle(viz_image, (x1, y1), (x2, y2), color, 2)
                
                # Draw label
                label_text = f"{label} ({confidence:.2f})"
                font_scale = 0.6
                thickness = 1
                font = cv2.FONT_HERSHEY_SIMPLEX
                
                # Get text size
                (text_width, text_height), baseline = cv2.getTextSize(label_text, font, font_scale, thickness)
                
                # Draw background rectangle for text
                cv2.rectangle(viz_image, (x1, y1 - text_height - 10), (x1 + text_width, y1), color, -1)
                
                # Draw text
                cv2.putText(viz_image, label_text, (x1, y1 - 5), font, font_scale, (0, 0, 0), thickness)
        
        # Draw SAM segmentation masks (if available)
        if "segments" in sam_results:
            segments = sam_results["segments"]
            for i, segment in enumerate(segments):
                mask = segment.get("mask")
                label = segment.get("label", f"segment_{i}")
                
                if mask is not None and len(mask.shape) == 2:
                    # Create colored mask
                    colored_mask = np.zeros_like(viz_image)
                    color = colors.get(label.lower(), colors["default"])
                    colored_mask[mask > 0] = color
                    
                    # Blend with original image
                    alpha = 0.3
                    viz_image = cv2.addWeighted(viz_image, 1 - alpha, colored_mask, alpha, 0)
                    
                    # Draw contour
                    contours, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    if contours:
                        cv2.drawContours(viz_image, contours, -1, color, 2)
        
        # Add legend
        legend_y = 30
        legend_x = width - 200
        
        # Draw legend background
        cv2.rectangle(viz_image, (legend_x - 10, legend_y - 20), (legend_x + 180, legend_y + 200), (0, 0, 0), -1)
        cv2.rectangle(viz_image, (legend_x - 10, legend_y - 20), (legend_x + 180, legend_y + 200), (255, 255, 255), 2)
        
        # Add legend text
        legend_items = [
            ("GPT Vision", colors["default"]),
            ("Room", colors["room"]),
            ("Door", colors["door"]),
            ("Window", colors["window"]),
            ("Kitchen", colors["kitchen"]),
            ("Bathroom", colors["bathroom"])
        ]
        
        for i, (text, color) in enumerate(legend_items):
            y_pos = legend_y + i * 25
            cv2.rectangle(viz_image, (legend_x, y_pos - 15), (legend_x + 15, y_pos), color, -1)
            cv2.putText(viz_image, text, (legend_x + 20, y_pos - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Add analysis summary
        summary_text = f"GPT Elements: {len(spatial_elements)} | SAM Segments: {len(sam_results.get('segments', []))}"
        cv2.putText(viz_image, summary_text, (10, height - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(viz_image, summary_text, (10, height - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
        
        return viz_image
    
    def analyze_image(self, image_path: str) -> Dict[str, Any]:
        """Complete analysis pipeline: GPT Vision + SAM"""
        
        print("🚀 Starting GPT-SAM analysis pipeline...")
        
        # Step 1: GPT Vision analysis
        print("🧠 Step 1: GPT Vision analysis...")
        gpt_analysis = self.analyze_with_coordinates(image_path)
        
        if "error" in gpt_analysis:
            return {"error": f"GPT Vision analysis failed: {gpt_analysis['error']}"}
        
        # Step 2: SAM segmentation
        print("🎨 Step 2: SAM segmentation...")
        sam_results = self.segment_with_sam(image_path, gpt_analysis)
        
        # Step 3: Create visualization
        print("📊 Step 3: Creating visualization...")
        viz_image = None
        if "error" not in sam_results:
            viz_image = self.create_visualization(image_path, gpt_analysis, sam_results)
        
        # Compile results
        results = {
            "gpt_analysis": gpt_analysis,
            "sam_results": sam_results,
            "visualization": viz_image,
            "analysis_timestamp": datetime.now().isoformat(),
            "pipeline_version": "gpt_sam_v1.0"
        }
        
        print("✅ GPT-SAM analysis complete!")
        return results 