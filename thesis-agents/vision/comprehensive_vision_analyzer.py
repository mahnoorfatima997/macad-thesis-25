"""
Comprehensive Vision Analysis Framework
Provides structured image analysis with classification, visual element extraction, and improvement recommendations.
"""

import os
import base64
import cv2
import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from PIL import Image
from openai import OpenAI


class ComprehensiveVisionAnalyzer:
    """
    Advanced vision analyzer that provides comprehensive image analysis including:
    - Image type classification (floor plan, elevation, 3D, etc.)
    - Visual element extraction (shapes, colors, spatial organization)
    - Detailed architectural analysis
    - Improvement recommendations
    """
    
    def __init__(self, domain: str = "architecture"):
        self.domain = domain
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Image classification categories
        self.image_types = [
            "floor_plan", "elevation", "section", "axonometric", "perspective", 
            "3d_rendering", "sketch", "photograph", "technical_drawing", "site_plan"
        ]
        
        self.drawing_mediums = [
            "hand_drawn", "digital_cad", "mixed_media", "photograph", "rendering", "pencil_sketch"
        ]
        
        self.detail_levels = [
            "conceptual_sketch", "schematic_design", "design_development", 
            "construction_document", "presentation_drawing"
        ]

    def encode_image(self, image_path: str) -> str:
        """Encode image to base64 for API transmission"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    async def analyze_image_comprehensive(self, image_path: str, context: str = "") -> Dict[str, Any]:
        """
        Perform comprehensive image analysis with structured output
        
        Args:
            image_path: Path to the image file
            context: Optional project context
            
        Returns:
            Comprehensive analysis dictionary with structured data
        """
        
        print(f"🔍 Starting comprehensive image analysis: {image_path}")
        
        try:
            # Encode image
            base64_image = self.encode_image(image_path)
            
            # Create comprehensive analysis prompt
            analysis_prompt = self._create_comprehensive_prompt(context)
            
            print("📤 Sending comprehensive analysis request to GPT-4V...")
            
            # Call GPT-4V for analysis
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": analysis_prompt},
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
                max_tokens=3000,
                temperature=0.2
            )
            
            raw_analysis = response.choices[0].message.content
            print("✅ Comprehensive analysis complete")
            
            # Structure the analysis
            structured_analysis = self._structure_analysis(raw_analysis, image_path)
            
            return structured_analysis
            
        except Exception as e:
            print(f"❌ Error in comprehensive analysis: {e}")
            return {
                "error": f"Analysis failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }

    def _create_comprehensive_prompt(self, context: str = "") -> str:
        """Create a comprehensive analysis prompt"""
        
        prompt = f"""
        You are an expert architectural visual analyst. Perform a systematic, comprehensive analysis of this image.

        STEP 1 - IMAGE CLASSIFICATION:
        Identify and specify:
        - IMAGE_TYPE: {' | '.join(self.image_types)}
        - DRAWING_MEDIUM: {' | '.join(self.drawing_mediums)}
        - DETAIL_LEVEL: {' | '.join(self.detail_levels)}
        - PERSPECTIVE_VIEW: plan_view | elevation_view | section_cut | isometric | perspective | bird_eye | other
        - DRAWING_STYLE: architectural_technical | artistic_sketch | presentation_quality | working_drawing

        STEP 2 - VISUAL ELEMENTS:
        Extract and describe:
        - DOMINANT_SHAPES: List main geometric forms and spatial configurations
        - COLOR_PALETTE: Describe colors used and their architectural significance
        - LINE_QUALITIES: Analyze line weights, styles, and drawing techniques
        - SPATIAL_ORGANIZATION: How spaces/elements are arranged and connected
        - SCALE_INDICATORS: Dimensions, scale bars, human figures, furniture for scale

        STEP 3 - ARCHITECTURAL CONTENT:
        Identify and analyze:
        - BUILDING_ELEMENTS: Walls, doors, windows, stairs, structural elements
        - SPATIAL_HIERARCHY: Organization and relationship of spaces
        - CIRCULATION_PATTERNS: Movement paths, entrances, connections
        - FUNCTIONAL_ZONES: Different program areas and their relationships
        - STRUCTURAL_SYSTEMS: Visible structural approach and elements

        STEP 4 - DESIGN ANALYSIS:
        Evaluate:
        - DESIGN_STRENGTHS: What works well and why (be specific)
        - IMPROVEMENT_OPPORTUNITIES: Specific, actionable enhancement suggestions
        - FUNCTIONAL_ASSESSMENT: How well it serves intended purposes
        - ACCESSIBILITY_CONSIDERATIONS: Universal design and inclusive access
        - SUSTAINABILITY_POTENTIAL: Environmental design opportunities

        STEP 5 - TECHNICAL QUALITY:
        Assess:
        - DRAWING_COMPLETENESS: Level of development and detail
        - TECHNICAL_ACCURACY: Proper use of conventions and standards
        - CLARITY_OF_COMMUNICATION: How well it conveys design intent
        - PROFESSIONAL_PRESENTATION: Quality of graphic communication

        FORMAT: Use clear section headers. Be specific and detailed. Avoid generic statements.
        """
        
        if context:
            prompt += f"\n\nPROJECT CONTEXT: {context}\nRelate your analysis to this specific context."
        
        return prompt

    def _structure_analysis(self, raw_analysis: str, image_path: str) -> Dict[str, Any]:
        """Structure the raw analysis into organized categories"""
        
        return {
            "raw_analysis": raw_analysis,
            "image_path": image_path,
            "timestamp": datetime.now().isoformat(),
            "classification": self._extract_classification(raw_analysis),
            "visual_elements": self._extract_visual_elements(raw_analysis),
            "architectural_content": self._extract_architectural_content(raw_analysis),
            "design_analysis": self._extract_design_analysis(raw_analysis),
            "technical_quality": self._extract_technical_quality(raw_analysis),
            "summary": self._generate_summary(raw_analysis),
            "confidence_score": self._calculate_confidence(raw_analysis)
        }

    def _extract_classification(self, analysis: str) -> Dict[str, str]:
        """Extract image classification data"""
        classification = {}
        
        patterns = {
            "image_type": ["IMAGE_TYPE:", "Type:", "Drawing type:"],
            "drawing_medium": ["DRAWING_MEDIUM:", "Medium:"],
            "detail_level": ["DETAIL_LEVEL:", "Detail level:"],
            "perspective_view": ["PERSPECTIVE_VIEW:", "View:", "Perspective:"],
            "drawing_style": ["DRAWING_STYLE:", "Style:"]
        }
        
        for key, search_terms in patterns.items():
            for term in search_terms:
                if term.lower() in analysis.lower():
                    lines = analysis.split('\n')
                    for line in lines:
                        if term.lower() in line.lower():
                            parts = line.split(':', 1)
                            if len(parts) > 1:
                                value = parts[1].strip().split()[0] if parts[1].strip() else "unknown"
                                classification[key] = value.replace('[', '').replace(']', '')
                                break
                    break
        
        return classification

    def _extract_visual_elements(self, analysis: str) -> Dict[str, str]:
        """Extract visual elements information"""
        return self._extract_section_content(analysis, [
            "DOMINANT_SHAPES", "COLOR_PALETTE", "LINE_QUALITIES", 
            "SPATIAL_ORGANIZATION", "SCALE_INDICATORS"
        ])

    def _extract_architectural_content(self, analysis: str) -> Dict[str, str]:
        """Extract architectural content information"""
        return self._extract_section_content(analysis, [
            "BUILDING_ELEMENTS", "SPATIAL_HIERARCHY", "CIRCULATION_PATTERNS",
            "FUNCTIONAL_ZONES", "STRUCTURAL_SYSTEMS"
        ])

    def _extract_design_analysis(self, analysis: str) -> Dict[str, str]:
        """Extract design analysis information"""
        return self._extract_section_content(analysis, [
            "DESIGN_STRENGTHS", "IMPROVEMENT_OPPORTUNITIES", "FUNCTIONAL_ASSESSMENT",
            "ACCESSIBILITY_CONSIDERATIONS", "SUSTAINABILITY_POTENTIAL"
        ])

    def _extract_technical_quality(self, analysis: str) -> Dict[str, str]:
        """Extract technical quality assessment"""
        return self._extract_section_content(analysis, [
            "DRAWING_COMPLETENESS", "TECHNICAL_ACCURACY", 
            "CLARITY_OF_COMMUNICATION", "PROFESSIONAL_PRESENTATION"
        ])

    def _extract_section_content(self, analysis: str, section_keys: List[str]) -> Dict[str, str]:
        """Helper method to extract content for specific sections"""
        content = {}
        
        for key in section_keys:
            search_terms = [f"{key}:", key.replace('_', ' ').title() + ":"]
            
            for term in search_terms:
                if term.lower() in analysis.lower():
                    lines = analysis.split('\n')
                    for i, line in enumerate(lines):
                        if term.lower() in line.lower():
                            # Extract content from this line and next few lines
                            extracted_content = line.split(':', 1)[1].strip() if ':' in line else ""
                            
                            # Look ahead for continuation
                            for j in range(1, 4):
                                if i + j < len(lines):
                                    next_line = lines[i + j].strip()
                                    if next_line and not any(s in next_line for s in ['STEP', ':', '-']) and not next_line.isupper():
                                        extracted_content += " " + next_line
                                    else:
                                        break
                            
                            content[key.lower()] = extracted_content
                            break
                    break
        
        return content

    def _generate_summary(self, analysis: str) -> str:
        """Generate a concise summary of the analysis"""
        # Extract key points for summary
        lines = analysis.split('\n')
        key_points = []
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ['main', 'primary', 'key', 'important', 'significant']):
                if len(line.strip()) > 20:  # Avoid very short lines
                    key_points.append(line.strip())
        
        if key_points:
            return " ".join(key_points[:3])  # Top 3 key points
        else:
            return "Comprehensive architectural analysis completed with detailed observations."

    def _calculate_confidence(self, analysis: str) -> float:
        """Calculate confidence score based on analysis depth and specificity"""
        word_count = len(analysis.split())
        specific_terms = ['specific', 'detailed', 'clear', 'evident', 'visible', 'shows', 'indicates']
        specificity_score = sum(1 for term in specific_terms if term in analysis.lower())
        
        # Normalize scores
        length_score = min(word_count / 500, 1.0)  # 500 words = full score
        specificity_normalized = min(specificity_score / 5, 1.0)  # 5 terms = full score
        
        confidence = (length_score * 0.6 + specificity_normalized * 0.4)
        return round(max(0.1, min(1.0, confidence)), 2)

    async def get_detailed_image_understanding(self, image_path: str, context: str = "") -> Dict[str, Any]:
        """
        Get detailed image understanding with specific architectural insights

        Args:
            image_path: Path to the image
            context: Optional project context

        Returns:
            Detailed understanding dictionary with specific insights
        """

        try:
            # Encode image
            base64_image = self.encode_image(image_path)

            # Create detailed understanding prompt for comprehensive visual description
            understanding_prompt = f"""
            You are an expert architectural analyst. Analyze this image and provide an extremely detailed visual description.

            PROVIDE A COMPREHENSIVE VISUAL DESCRIPTION:

            1. IMMEDIATE VISUAL DESCRIPTION:
            - Describe exactly what you see in rich visual detail (like describing to someone who cannot see the image)
            - Include colors, textures, materials, lighting, shadows, and spatial qualities
            - Describe the viewpoint, perspective, and framing of the image
            - Note the overall composition and visual hierarchy

            2. ARCHITECTURAL ELEMENTS AND SPACES:
            - Describe all visible architectural elements with specific details (walls, floors, ceilings, openings, etc.)
            - Identify and describe any furniture, fixtures, or objects present
            - Describe spatial relationships, proportions, and scale indicators
            - Note circulation paths, entries, transitions between spaces

            3. MATERIALS AND FINISHES:
            - Identify and describe all visible materials (concrete, wood, tile, glass, metal, etc.)
            - Describe surface treatments, textures, patterns, and finishes
            - Note any material combinations or contrasts
            - Describe how materials contribute to the overall aesthetic

            4. LIGHTING AND ATMOSPHERE:
            - Describe the lighting conditions (natural, artificial, quality of light)
            - Note shadows, reflections, and how light interacts with surfaces
            - Describe the overall mood or atmosphere created
            - Identify light sources and their effects

            5. SPECIFIC DETAILS AND FEATURES:
            - Point out any distinctive design features, details, or elements
            - Describe any visible technology, systems, or equipment
            - Note any text, signage, or graphic elements
            - Identify any people, activities, or signs of use

            Write as if you are describing the scene to someone who cannot see it. Be extremely specific about what you observe. Use rich, descriptive language that captures both the technical and experiential qualities of the space.
            """

            if context:
                understanding_prompt += f"\n\nPROJECT CONTEXT: {context}\nRelate your analysis specifically to this project context."

            print("📤 Sending detailed understanding request to GPT-4V...")

            # Call GPT-4V for detailed understanding
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": understanding_prompt},
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
                max_tokens=3000,
                temperature=0.1  # Very low temperature for factual analysis
            )

            detailed_understanding = response.choices[0].message.content
            print("✅ Detailed understanding complete")

            # Extract key insights for chat integration
            key_insights = self._extract_key_insights(detailed_understanding)

            return {
                "detailed_analysis": detailed_understanding,
                "key_insights": key_insights,
                "chat_summary": self._create_chat_summary(key_insights),
                "timestamp": datetime.now().isoformat(),
                "confidence": self._calculate_understanding_confidence(detailed_understanding)
            }

        except Exception as e:
            print(f"❌ Error in detailed understanding: {e}")
            return {
                "error": f"Detailed understanding failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }

    def _extract_key_insights(self, analysis: str) -> Dict[str, str]:
        """Extract key insights from detailed visual analysis"""
        insights = {}

        # Store the full detailed analysis for rich context
        insights["detailed_visual_description"] = analysis

        # Extract specific visual elements for system understanding
        sections = {
            "space_type": ["room", "space", "interior", "exterior", "view of"],
            "materials": ["material", "concrete", "wood", "tile", "glass", "metal", "stone", "brick"],
            "lighting": ["light", "lighting", "illuminated", "bright", "shadow", "natural light"],
            "colors": ["color", "white", "grey", "black", "brown", "blue", "green", "red"],
            "textures": ["texture", "smooth", "rough", "polished", "matte", "glossy"],
            "furniture": ["furniture", "chair", "table", "desk", "sofa", "bed", "cabinet"],
            "architectural_elements": ["wall", "floor", "ceiling", "window", "door", "column", "beam"],
            "key_features": ["features", "notable", "distinctive", "prominent", "visible"]
        }

        analysis_lower = analysis.lower()

        for key, search_terms in sections.items():
            descriptive_parts = []
            sentences = analysis.split('.')

            for sentence in sentences:
                sentence_lower = sentence.lower()
                for term in search_terms:
                    if term in sentence_lower and len(sentence.strip()) > 15:
                        # Clean and add descriptive sentence
                        clean_sentence = sentence.strip()
                        if clean_sentence and clean_sentence not in descriptive_parts:
                            descriptive_parts.append(clean_sentence)
                        break

            if descriptive_parts:
                # Take the most descriptive sentence for this category
                insights[key] = descriptive_parts[0]

        return insights

    def _create_chat_summary(self, insights: Dict[str, str]) -> str:
        """Create a detailed visual description for system understanding"""

        # Instead of a generic template, use the full detailed analysis
        # This provides rich context for the routing system to understand the image
        detailed_description = insights.get("detailed_visual_description", "")

        if detailed_description:
            # Extract the most descriptive parts for system context
            # Take first few sentences that contain the most visual detail
            sentences = detailed_description.split('. ')

            # Select sentences that contain rich visual descriptions
            descriptive_sentences = []
            for sentence in sentences[:5]:  # Take up to 5 sentences
                if any(keyword in sentence.lower() for keyword in [
                    'shows', 'displays', 'features', 'contains', 'reveals', 'depicts',
                    'room', 'space', 'wall', 'floor', 'ceiling', 'window', 'door',
                    'material', 'texture', 'color', 'light', 'shadow'
                ]):
                    descriptive_sentences.append(sentence.strip())

            if descriptive_sentences:
                return '. '.join(descriptive_sentences) + '.'

        # Fallback to extracting key visual elements
        visual_elements = []
        for key, value in insights.items():
            if key in ['space_type', 'materials', 'lighting', 'key_features'] and value:
                visual_elements.append(value)

        if visual_elements:
            return f"The image shows {', '.join(visual_elements[:3])}."

        return "A detailed architectural image with specific design elements and spatial qualities."

    def _clean_insight_text(self, text: str) -> str:
        """Clean insight text for conversational use"""
        if not text:
            return "architectural content"

        # Remove common prefixes and make more conversational
        text = text.replace("This is", "").replace("The image shows", "").replace("I can see", "")
        text = text.replace("- ", "").strip()

        # Take first meaningful part
        if '.' in text:
            text = text.split('.')[0]
        if ',' in text and len(text.split(',')[0]) > 10:
            text = text.split(',')[0]

        return text.strip().lower()

    def _calculate_understanding_confidence(self, analysis: str) -> float:
        """Calculate confidence based on specificity and detail"""

        # Count specific architectural terms
        specific_terms = [
            'floor plan', 'elevation', 'section', 'axonometric', 'perspective',
            'residential', 'commercial', 'institutional', 'mixed-use',
            'circulation', 'entry', 'lobby', 'corridor', 'stair', 'elevator',
            'structural', 'column', 'beam', 'wall', 'window', 'door',
            'spatial', 'proportion', 'scale', 'hierarchy', 'organization'
        ]

        analysis_lower = analysis.lower()
        term_count = sum(1 for term in specific_terms if term in analysis_lower)

        # Count detailed observations
        detail_indicators = ['specifically', 'precisely', 'notably', 'particularly', 'clearly visible']
        detail_count = sum(1 for indicator in detail_indicators if indicator in analysis_lower)

        # Calculate confidence
        term_score = min(term_count / 10, 1.0)  # 10 terms = full score
        detail_score = min(detail_count / 3, 1.0)  # 3 details = full score
        length_score = min(len(analysis.split()) / 300, 1.0)  # 300 words = full score

        confidence = (term_score * 0.4 + detail_score * 0.3 + length_score * 0.3)
        return round(max(0.2, min(1.0, confidence)), 2)

    async def get_image_description_for_chat(self, image_path: str, context: str = "") -> str:
        """
        Get a specific image description suitable for chat context

        Args:
            image_path: Path to the image
            context: Optional context

        Returns:
            Specific description showing real understanding
        """

        try:
            # Get detailed understanding
            understanding = await self.get_detailed_image_understanding(image_path, context)

            if "error" in understanding:
                return f"Image analysis error: {understanding['error']}"

            # Return the specific chat summary
            return understanding.get("chat_summary", "Architectural analysis completed with detailed observations.")

        except Exception as e:
            return f"Unable to analyze image: {str(e)}"
