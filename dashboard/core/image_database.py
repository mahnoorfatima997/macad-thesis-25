"""
Image Database System for storing and retrieving image analysis data.

This module provides functionality to analyze uploaded images and store
the analysis results in categories for later reference throughout conversations.
"""

import os
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any
from PIL import Image
import tempfile


class ImageDatabase:
    """Database for storing and retrieving image analysis data."""
    
    def __init__(self, storage_path: str = None):
        """Initialize the image database."""
        if storage_path is None:
            storage_path = os.path.join(tempfile.gettempdir(), "mentor_image_db")
        
        self.storage_path = storage_path
        self.ensure_storage_directory()
        
    def ensure_storage_directory(self):
        """Ensure the storage directory exists."""
        os.makedirs(self.storage_path, exist_ok=True)
        
    def generate_image_id(self, image_path: str) -> str:
        """Generate a unique ID for an image based on its content."""
        with open(image_path, 'rb') as f:
            image_hash = hashlib.md5(f.read()).hexdigest()
        return f"img_{image_hash[:12]}"
    
    def analyze_image(self, image_path: str, user_context: str = "") -> Dict[str, Any]:
        """Analyze an image and extract metadata in categories."""
        try:
            # Open and analyze the image
            image = Image.open(image_path)
            
            # Basic image properties
            width, height = image.size
            format_type = image.format or "Unknown"
            mode = image.mode
            
            # Generate analysis categories
            analysis = {
                "technical_properties": {
                    "width": width,
                    "height": height,
                    "format": format_type,
                    "mode": mode,
                    "aspect_ratio": round(width / height, 2) if height > 0 else 0,
                    "file_size": os.path.getsize(image_path) if os.path.exists(image_path) else 0
                },
                "architectural_elements": {
                    "drawing_type": self._detect_drawing_type(image, user_context),
                    "scale_indicators": self._detect_scale_elements(image),
                    "structural_elements": self._detect_structural_elements(image),
                    "spatial_organization": self._analyze_spatial_organization(image)
                },
                "design_characteristics": {
                    "line_quality": self._analyze_line_quality(image),
                    "detail_level": self._assess_detail_level(image),
                    "drawing_style": self._identify_drawing_style(image),
                    "completeness": self._assess_completeness(image)
                },
                "contextual_information": {
                    "user_context": user_context,
                    "upload_timestamp": datetime.now().isoformat(),
                    "analysis_version": "1.0"
                }
            }
            
            return analysis
            
        except Exception as e:
            return {
                "error": f"Failed to analyze image: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def _detect_drawing_type(self, image: Image.Image, context: str) -> str:
        """Detect the type of architectural drawing."""
        # Simple heuristic based on aspect ratio and context
        width, height = image.size
        aspect_ratio = width / height if height > 0 else 1
        
        context_lower = context.lower()
        
        if "floor plan" in context_lower or "plan" in context_lower:
            return "floor_plan"
        elif "elevation" in context_lower or "facade" in context_lower:
            return "elevation"
        elif "section" in context_lower:
            return "section"
        elif "sketch" in context_lower or "concept" in context_lower:
            return "conceptual_sketch"
        elif "detail" in context_lower:
            return "detail_drawing"
        elif aspect_ratio > 1.5:
            return "elevation_or_section"
        elif 0.7 <= aspect_ratio <= 1.3:
            return "floor_plan_or_site_plan"
        else:
            return "architectural_drawing"
    
    def _detect_scale_elements(self, image: Image.Image) -> List[str]:
        """Detect scale-related elements in the drawing."""
        # Placeholder for scale detection logic
        return ["scale_bar_possible", "dimension_lines_detected"]
    
    def _detect_structural_elements(self, image: Image.Image) -> List[str]:
        """Detect structural elements in the drawing."""
        # Placeholder for structural element detection
        return ["walls", "openings", "structural_grid"]
    
    def _analyze_spatial_organization(self, image: Image.Image) -> Dict[str, Any]:
        """Analyze spatial organization of the drawing."""
        width, height = image.size
        return {
            "composition": "centered" if width > height else "vertical",
            "complexity": "medium",
            "organization_type": "orthogonal"
        }
    
    def _analyze_line_quality(self, image: Image.Image) -> str:
        """Analyze the quality of lines in the drawing."""
        # Placeholder for line quality analysis
        return "hand_drawn" if image.mode in ["L", "RGB"] else "digital"
    
    def _assess_detail_level(self, image: Image.Image) -> str:
        """Assess the level of detail in the drawing."""
        # Simple heuristic based on image complexity
        width, height = image.size
        total_pixels = width * height
        
        if total_pixels > 1000000:  # High resolution
            return "high_detail"
        elif total_pixels > 500000:
            return "medium_detail"
        else:
            return "low_detail"
    
    def _identify_drawing_style(self, image: Image.Image) -> str:
        """Identify the drawing style."""
        # Placeholder for style identification
        return "technical_drawing" if image.mode == "L" else "mixed_media"
    
    def _assess_completeness(self, image: Image.Image) -> str:
        """Assess how complete the drawing appears."""
        # Placeholder for completeness assessment
        return "partial_sketch"  # Default assumption

    def store_image_analysis(self, image_path: str, analysis: Dict[str, Any]) -> str:
        """Store image analysis data and return the image ID."""
        image_id = self.generate_image_id(image_path)

        # Create storage record
        record = {
            "image_id": image_id,
            "original_path": image_path,
            "analysis": analysis,
            "stored_timestamp": datetime.now().isoformat()
        }

        # Save to JSON file
        record_path = os.path.join(self.storage_path, f"{image_id}.json")
        with open(record_path, 'w') as f:
            json.dump(record, f, indent=2)

        print(f"📁 Stored image analysis: {image_id}")
        return image_id

    def get_image_analysis(self, image_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve stored image analysis by ID."""
        record_path = os.path.join(self.storage_path, f"{image_id}.json")

        if not os.path.exists(record_path):
            return None

        try:
            with open(record_path, 'r') as f:
                record = json.load(f)
            return record.get("analysis")
        except Exception as e:
            print(f"❌ Error retrieving image analysis {image_id}: {e}")
            return None

    def search_images_by_type(self, drawing_type: str) -> List[str]:
        """Search for images by drawing type."""
        matching_ids = []

        for filename in os.listdir(self.storage_path):
            if filename.endswith('.json'):
                image_id = filename[:-5]  # Remove .json extension
                analysis = self.get_image_analysis(image_id)

                if analysis and analysis.get("architectural_elements", {}).get("drawing_type") == drawing_type:
                    matching_ids.append(image_id)

        return matching_ids

    def get_conversation_images(self) -> List[Dict[str, Any]]:
        """Get all images from the current conversation session."""
        images = []

        for filename in os.listdir(self.storage_path):
            if filename.endswith('.json'):
                image_id = filename[:-5]
                record_path = os.path.join(self.storage_path, filename)

                try:
                    with open(record_path, 'r') as f:
                        record = json.load(f)

                    # Add summary info for conversation reference
                    summary = {
                        "image_id": image_id,
                        "drawing_type": record.get("analysis", {}).get("architectural_elements", {}).get("drawing_type", "unknown"),
                        "upload_time": record.get("analysis", {}).get("contextual_information", {}).get("upload_timestamp"),
                        "user_context": record.get("analysis", {}).get("contextual_information", {}).get("user_context", ""),
                        "technical_summary": self._create_technical_summary(record.get("analysis", {}))
                    }
                    images.append(summary)

                except Exception as e:
                    print(f"❌ Error reading image record {filename}: {e}")

        # Sort by upload time (most recent first)
        images.sort(key=lambda x: x.get("upload_time", ""), reverse=True)
        return images

    def _create_technical_summary(self, analysis: Dict[str, Any]) -> str:
        """Create a brief technical summary of the image."""
        tech_props = analysis.get("technical_properties", {})
        design_chars = analysis.get("design_characteristics", {})

        width = tech_props.get("width", 0)
        height = tech_props.get("height", 0)
        detail_level = design_chars.get("detail_level", "unknown")

        return f"{width}x{height}px, {detail_level} detail"

    def reference_image_in_context(self, image_id: str, context: str) -> str:
        """Generate a contextual reference to a stored image."""
        analysis = self.get_image_analysis(image_id)

        if not analysis:
            return f"[Referenced image {image_id} - analysis not available]"

        drawing_type = analysis.get("architectural_elements", {}).get("drawing_type", "drawing")
        detail_level = analysis.get("design_characteristics", {}).get("detail_level", "unknown")

        return f"[Referencing your {drawing_type} ({detail_level} detail) from earlier in our conversation]"
