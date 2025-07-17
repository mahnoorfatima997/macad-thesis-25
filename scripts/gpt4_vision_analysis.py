#!/usr/bin/env python3
"""
GPT-4 Vision Analysis Module
Replaces Magma with OpenAI's GPT-4 Vision for semantic analysis of site plans
"""

import os
import base64
import json
from typing import Dict, Any, Optional
from PIL import Image
import requests
from openai import OpenAI
from dotenv import load_dotenv

# Set up E drive environment first
from utils.e_drive_setup import setup_e_drive_environment
setup_e_drive_environment()

# Load environment variables
load_dotenv()

class GPT4VisionAnalyzer:
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize GPT-4 Vision analyzer
        
        Args:
            api_key (str, optional): OpenAI API key. If not provided, will use OPENAI_API_KEY env var
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
        
        self.client = OpenAI(api_key=self.api_key)
        
        # Set up E drive cache for any temporary files
        e_cache_dir = setup_e_drive_environment()
        self.temp_dir = os.path.join(e_cache_dir, "gpt4_temp")
        os.makedirs(self.temp_dir, exist_ok=True)
        
    def _encode_image_to_base64(self, image_path: str) -> str:
        """
        Encode image to base64 string for GPT-4 Vision API
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            str: Base64 encoded image
        """
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            raise ValueError(f"Error encoding image {image_path}: {e}")
    
    def _preprocess_image_for_gpt4(self, image_path: str) -> str:
        """
        Preprocess image for GPT-4 Vision analysis
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            str: Path to preprocessed image
        """
        try:
            # Load and resize image for optimal GPT-4 Vision performance
            image = Image.open(image_path)
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize to reasonable size (GPT-4 Vision works well with 1024x1024 or smaller)
            max_size = 1024
            if max(image.size) > max_size:
                ratio = max_size / max(image.size)
                new_size = tuple(int(dim * ratio) for dim in image.size)
                image = image.resize(new_size, Image.Resampling.LANCZOS)
            
            # Save preprocessed image to E drive temp directory
            filename = os.path.basename(image_path)
            name, ext = os.path.splitext(filename)
            output_path = os.path.join(self.temp_dir, f"{name}_gpt4{ext}")
            image.save(output_path, quality=95)
            
            return output_path
            
        except Exception as e:
            print(f"Warning: Could not preprocess image, using original: {e}")
            return image_path
    
    def analyze_with_gpt4_vision(self, image_path: str, query: str, max_tokens: int = 1000) -> str:
        """
        Analyze an image using GPT-4 Vision with a specific query
        
        Args:
            image_path (str): Path to the image file
            query (str): Query/question about the image
            max_tokens (int): Maximum number of tokens to generate
            
        Returns:
            str: Generated response from GPT-4 Vision
        """
        try:
            # Preprocess image
            processed_image_path = self._preprocess_image_for_gpt4(image_path)
            
            # Encode image
            base64_image = self._encode_image_to_base64(processed_image_path)
            
            # Create API request
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": query
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=max_tokens,
                temperature=0.1  # Low temperature for more consistent analysis
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error analyzing image with GPT-4 Vision: {str(e)}"
    
    def analyze_site_plan_constraints(self, image_path: str) -> Dict[str, Any]:
        """
        Analyze site plan for spatial constraints and design issues
        
        Args:
            image_path (str): Path to the site plan image
            
        Returns:
            dict: Analysis results with different aspects
        """
        analysis_results = {}
        
        # Define analysis queries for comprehensive site plan evaluation
        queries = {
            "spatial_constraints": """
            Analyze this site plan for spatial constraints and design issues. Consider:
            - Building placement and orientation
            - Site access and circulation
            - Zoning compliance issues
            - Environmental constraints
            - Functional relationships between elements
            Provide specific observations and potential problems.
            """,
            
            "building_elements": """
            Identify and analyze the buildings and structures in this site plan:
            - Building types and functions
            - Size and scale relationships
            - Architectural features
            - Construction considerations
            - Integration with site context
            """,
            
            "site_features": """
            Analyze the natural and man-made features of this site:
            - Topography and drainage
            - Vegetation and landscaping
            - Existing infrastructure
            - Environmental features
            - Site boundaries and access points
            """,
            
            "access_circulation": """
            Evaluate the access and circulation patterns in this site plan:
            - Vehicle access and parking
            - Pedestrian circulation
            - Service access
            - Emergency vehicle access
            - Traffic flow and safety considerations
            """,
            
            "zoning_compliance": """
            Assess potential zoning and regulatory compliance issues:
            - Setback requirements
            - Building height restrictions
            - Land use compatibility
            - Parking requirements
            - Environmental regulations
            - Accessibility requirements
            """
        }
        
        print("Starting GPT-4 Vision analysis...")
        
        for aspect, query in queries.items():
            try:
                print(f"Analyzing {aspect}...")
                response = self.analyze_with_gpt4_vision(image_path, query)
                analysis_results[aspect] = response
                print(f"✓ {aspect} analysis completed")
            except Exception as e:
                analysis_results[aspect] = f"Error analyzing {aspect}: {str(e)}"
                print(f"✗ Error in {aspect} analysis: {e}")
        
        return analysis_results
    
    def generate_design_recommendations(self, image_path: str) -> str:
        """
        Generate specific design recommendations based on site plan analysis
        
        Args:
            image_path (str): Path to the site plan image
            
        Returns:
            str: Design recommendations
        """
        query = """
        Based on this site plan, provide specific design recommendations for improvement:
        
        1. **Site Planning**: How could the overall site layout be improved?
        2. **Building Design**: What architectural modifications would enhance the design?
        3. **Landscaping**: What landscape improvements would benefit the project?
        4. **Sustainability**: What sustainable design features could be incorporated?
        5. **Accessibility**: How could accessibility be improved?
        6. **Cost-Effectiveness**: What changes would provide the best value?
        
        Provide practical, actionable recommendations with brief explanations.
        """
        
        return self.analyze_with_gpt4_vision(image_path, query, max_tokens=1500)
    
    def analyze_with_yolo_context(self, image_path: str, yolo_detections: Dict[str, Any]) -> str:
        """
        Analyze image with context from YOLO detections
        
        Args:
            image_path (str): Path to the image file
            yolo_detections (dict): Results from YOLO object detection
            
        Returns:
            str: Enhanced analysis incorporating YOLO findings
        """
        # Create context from YOLO detections
        detection_summary = yolo_detections.get('summary', {})
        detection_counts = detection_summary.get('detection_summary', {})
        
        context = f"""
        YOLO Object Detection Results:
        - Total detections: {detection_summary.get('total_detections', 0)}
        - High confidence detections: {detection_summary.get('high_confidence_detections', 0)}
        - Detected elements: {', '.join([f'{k}: {v}' for k, v in detection_counts.items()])}
        
        Please analyze this site plan considering the detected elements above. 
        Focus on how these elements interact and what design implications they suggest.
        """
        
        return self.analyze_with_gpt4_vision(image_path, context, max_tokens=1200)
    
    def cleanup_temp_files(self):
        """
        Clean up temporary files created during analysis
        """
        try:
            if os.path.exists(self.temp_dir):
                for file in os.listdir(self.temp_dir):
                    file_path = os.path.join(self.temp_dir, file)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                print(f"✓ Cleaned up temporary files in: {self.temp_dir}")
        except Exception as e:
            print(f"Warning: Could not clean up temp files: {e}")


# Global analyzer instance
gpt4_analyzer = GPT4VisionAnalyzer()

def analyze_with_gpt4_vision(image_path: str, query: str) -> str:
    """
    Convenience function for quick GPT-4 Vision analysis
    
    Args:
        image_path (str): Path to the image file
        query (str): Query/question about the image
        
    Returns:
        str: Generated response
    """
    return gpt4_analyzer.analyze_with_gpt4_vision(image_path, query)

def analyze_site_plan_semantics(image_path: str) -> Dict[str, Any]:
    """
    Complete semantic analysis of a site plan using GPT-4 Vision
    
    Args:
        image_path (str): Path to the site plan image
        
    Returns:
        dict: Comprehensive semantic analysis results
    """
    return gpt4_analyzer.analyze_site_plan_constraints(image_path)

def generate_design_recommendations(image_path: str) -> str:
    """
    Generate design recommendations using GPT-4 Vision
    
    Args:
        image_path (str): Path to the site plan image
        
    Returns:
        str: Design recommendations
    """
    return gpt4_analyzer.generate_design_recommendations(image_path) 