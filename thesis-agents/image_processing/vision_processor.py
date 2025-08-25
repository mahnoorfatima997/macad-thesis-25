"""
Image Vision Processing Module
Handles image upload, GPT Vision analysis, and data extraction for architectural design images.
"""

import os
import base64
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from openai import OpenAI
import streamlit as st
from PIL import Image
import io

@dataclass
class ImageAnalysis:
    """Results from GPT Vision analysis of an uploaded image"""
    image_id: str
    filename: str
    analysis_text: str
    design_elements: Dict[str, Any]
    building_type: Optional[str]
    design_phase: str
    architectural_features: List[str]
    materials_identified: List[str]
    spatial_organization: Dict[str, Any]
    technical_details: List[str]
    design_intent: str
    suggestions: List[str]
    confidence_score: float
    timestamp: datetime
    image_path: str

class VisionProcessor:
    """Handles image processing and GPT Vision analysis"""
    
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.image_storage_path = "thesis_data/uploaded_images"
        os.makedirs(self.image_storage_path, exist_ok=True)
    
    def encode_image_to_base64(self, image_path: str) -> str:
        """Encode image to base64 for GPT Vision API"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def save_uploaded_image(self, uploaded_file) -> str:
        """Save uploaded image and return file path"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{uploaded_file.name}"
        file_path = os.path.join(self.image_storage_path, filename)
        
        # Save the image
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        return file_path
    
    async def analyze_image(self, image_path: str, context: Dict[str, Any] = None) -> ImageAnalysis:
        """Analyze uploaded image using GPT Vision"""
        
        # Encode image
        base64_image = self.encode_image_to_base64(image_path)
        
        # Get context information
        current_phase = context.get('current_phase', 'unknown') if context else 'unknown'
        building_type = context.get('building_type', 'unknown') if context else 'unknown'
        conversation_context = context.get('conversation_summary', '') if context else ''
        
        # Create comprehensive analysis prompt
        prompt = f"""
        You are an expert architectural analyst. Analyze this architectural image in detail and extract comprehensive information.
        
        CONTEXT:
        - Current design phase: {current_phase}
        - Building type: {building_type}
        - Conversation context: {conversation_context}
        
        Please provide a detailed analysis covering:
        
        1. DESIGN ELEMENTS:
           - Architectural style and approach
           - Composition and layout principles
           - Scale and proportion analysis
           - Visual hierarchy and focal points
        
        2. BUILDING IDENTIFICATION:
           - Building type (residential, commercial, institutional, etc.)
           - Program and functional requirements evident
           - User groups and occupancy patterns
        
        3. DESIGN PHASE ASSESSMENT:
           - Is this conceptual sketches (ideation)?
           - Is this spatial planning/diagrams (visualization)?
           - Is this detailed design/construction (materialization)?
        
        4. ARCHITECTURAL FEATURES:
           - Structural systems visible
           - Circulation patterns
           - Spatial relationships
           - Environmental considerations
        
        5. MATERIALS AND CONSTRUCTION:
           - Materials identified or suggested
           - Construction methods evident
           - Technical details visible
           - Sustainability features
        
        6. SPATIAL ORGANIZATION:
           - Public vs private spaces
           - Interior vs exterior relationships
           - Vertical vs horizontal organization
           - Flexibility and adaptability
        
        7. DESIGN INTENT:
           - What problem is this design solving?
           - What are the key design goals?
           - How does it respond to context?
        
        8. EDUCATIONAL FEEDBACK:
           - Strengths of the design approach
           - Areas for development
           - Suggestions for next steps
           - Questions to explore further
        
        Return your analysis as a JSON object with this structure:
        {{
            "analysis_text": "Comprehensive written analysis",
            "design_elements": {{
                "style": "...",
                "composition": "...",
                "scale": "...",
                "hierarchy": "..."
            }},
            "building_type": "...",
            "design_phase": "ideation|visualization|materialization",
            "architectural_features": ["feature1", "feature2", ...],
            "materials_identified": ["material1", "material2", ...],
            "spatial_organization": {{
                "public_private": "...",
                "interior_exterior": "...",
                "circulation": "...",
                "flexibility": "..."
            }},
            "technical_details": ["detail1", "detail2", ...],
            "design_intent": "What this design is trying to achieve",
            "suggestions": ["suggestion1", "suggestion2", ...],
            "confidence_score": 0.85
        }}
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
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=2000,
                temperature=0.3
            )
            
            # Parse the JSON response
            analysis_json = json.loads(response.choices[0].message.content)
            
            # Create ImageAnalysis object
            image_id = f"img_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            filename = os.path.basename(image_path)
            
            return ImageAnalysis(
                image_id=image_id,
                filename=filename,
                analysis_text=analysis_json.get("analysis_text", ""),
                design_elements=analysis_json.get("design_elements", {}),
                building_type=analysis_json.get("building_type"),
                design_phase=analysis_json.get("design_phase", "unknown"),
                architectural_features=analysis_json.get("architectural_features", []),
                materials_identified=analysis_json.get("materials_identified", []),
                spatial_organization=analysis_json.get("spatial_organization", {}),
                technical_details=analysis_json.get("technical_details", []),
                design_intent=analysis_json.get("design_intent", ""),
                suggestions=analysis_json.get("suggestions", []),
                confidence_score=analysis_json.get("confidence_score", 0.5),
                timestamp=datetime.now(),
                image_path=image_path
            )
            
        except Exception as e:
            print(f"Image analysis failed: {e}")
            # Return basic analysis
            return ImageAnalysis(
                image_id=f"img_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                filename=os.path.basename(image_path),
                analysis_text=f"Image uploaded successfully. Analysis failed: {str(e)}",
                design_elements={},
                building_type="unknown",
                design_phase="unknown",
                architectural_features=[],
                materials_identified=[],
                spatial_organization={},
                technical_details=[],
                design_intent="Unable to analyze design intent",
                suggestions=["Please try uploading the image again"],
                confidence_score=0.1,
                timestamp=datetime.now(),
                image_path=image_path
            )
    
    def store_image_analysis(self, analysis: ImageAnalysis) -> str:
        """Store image analysis results to JSON file"""
        analysis_data = {
            "image_id": analysis.image_id,
            "filename": analysis.filename,
            "analysis_text": analysis.analysis_text,
            "design_elements": analysis.design_elements,
            "building_type": analysis.building_type,
            "design_phase": analysis.design_phase,
            "architectural_features": analysis.architectural_features,
            "materials_identified": analysis.materials_identified,
            "spatial_organization": analysis.spatial_organization,
            "technical_details": analysis.technical_details,
            "design_intent": analysis.design_intent,
            "suggestions": analysis.suggestions,
            "confidence_score": analysis.confidence_score,
            "timestamp": analysis.timestamp.isoformat(),
            "image_path": analysis.image_path
        }
        
        # Save to JSON file
        analysis_file = os.path.join(self.image_storage_path, f"{analysis.image_id}_analysis.json")
        with open(analysis_file, 'w') as f:
            json.dump(analysis_data, f, indent=2)
        
        return analysis_file
    
    def get_stored_analyses(self) -> List[ImageAnalysis]:
        """Retrieve all stored image analyses"""
        analyses = []
        
        for filename in os.listdir(self.image_storage_path):
            if filename.endswith("_analysis.json"):
                file_path = os.path.join(self.image_storage_path, filename)
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                    
                    analysis = ImageAnalysis(
                        image_id=data["image_id"],
                        filename=data["filename"],
                        analysis_text=data["analysis_text"],
                        design_elements=data["design_elements"],
                        building_type=data["building_type"],
                        design_phase=data["design_phase"],
                        architectural_features=data["architectural_features"],
                        materials_identified=data["materials_identified"],
                        spatial_organization=data["spatial_organization"],
                        technical_details=data["technical_details"],
                        design_intent=data["design_intent"],
                        suggestions=data["suggestions"],
                        confidence_score=data["confidence_score"],
                        timestamp=datetime.fromisoformat(data["timestamp"]),
                        image_path=data["image_path"]
                    )
                    analyses.append(analysis)
                except Exception as e:
                    print(f"Failed to load analysis {filename}: {e}")
        
        return sorted(analyses, key=lambda x: x.timestamp, reverse=True)
