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
from .image_analysis_cache import get_image_cache


class ComprehensiveVisionAnalyzer:
    """
    Advanced vision analyzer that provides comprehensive image analysis including:
    - Image type classification (floor plan, elevation, 3D, etc.)
    - Visual element extraction (shapes, colors, spatial organization)
    - Detailed architectural analysis
    - Improvement recommendations
    """
    
    def __init__(self, domain: str = "architecture", use_cache: bool = True):
        self.domain = domain
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.use_cache = use_cache

        # Initialize cache if enabled
        if self.use_cache:
            self.cache = get_image_cache()
            print("🗄️ Vision analyzer initialized with caching enabled")
        else:
            self.cache = None
            print("⚠️ Vision analyzer initialized with caching disabled")

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

        # Check cache first if enabled
        if self.use_cache and self.cache:
            cache_key = f"comprehensive_{context}"
            cached_result = self.cache.get_cached_analysis(image_path)
            if cached_result and cache_key in cached_result:
                print("⚡ Using cached comprehensive analysis")
                return cached_result[cache_key]

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

            # Cache the result if caching is enabled
            if self.use_cache and self.cache:
                cache_key = f"comprehensive_{context}"
                cached_result = self.cache.get_cached_analysis(image_path) or {}
                cached_result[cache_key] = structured_analysis
                self.cache.cache_analysis(image_path, cached_result)

            return structured_analysis

        except Exception as e:
            print(f"❌ Error in comprehensive analysis: {e}")
            return {
                "error": f"Analysis failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }

    def _create_comprehensive_prompt(self, context: str = "") -> str:
        """Create an enhanced comprehensive analysis prompt with contextual understanding"""

        prompt = f"""
        You are an expert architectural mentor and visual analyst with deep knowledge of design processes, spatial relationships, and architectural representation.

        Analyze this architectural image comprehensively and provide detailed insights that will help guide an architectural design conversation.

        ANALYSIS INSTRUCTIONS:
        1. Study the image carefully and identify all visible elements with precision
        2. Consider the drawing type, style, and level of development
        3. Analyze spatial relationships, proportions, and design intent
        4. Provide contextual feedback and suggestions
        5. Create a conversational response that demonstrates deep understanding
        6. Reference specific elements you can see in the image

        STEP 1 - IMAGE CLASSIFICATION:
        Identify and specify:
        - IMAGE_TYPE: {' | '.join(self.image_types)}
        - DRAWING_MEDIUM: {' | '.join(self.drawing_mediums)}
        - DETAIL_LEVEL: {' | '.join(self.detail_levels)}
        - PERSPECTIVE_VIEW: plan_view | elevation_view | section_cut | isometric | perspective | bird_eye | other
        - DRAWING_STYLE: architectural_technical | artistic_sketch | presentation_quality | working_drawing
        - DEVELOPMENT_LEVEL: schematic | design_development | construction_documents | conceptual | preliminary

        STEP 2 - SPATIAL ANALYSIS:
        Extract and analyze:
        - PRIMARY_SPACES: Specific spaces with approximate functions and relationships
        - CIRCULATION_PATTERNS: Detailed description of movement, flow, and connections between spaces
        - SPATIAL_HIERARCHY: How spaces are organized, prioritized, and relate to each other
        - INDOOR_OUTDOOR_RELATIONSHIPS: Specific connections between interior and exterior spaces
        - SPATIAL_SEQUENCES: How one moves through and experiences the spaces progressively
        - SCALE_AND_PROPORTION: Assessment of proportional relationships and their effectiveness

        STEP 3 - DESIGN ELEMENTS:
        Identify and analyze:
        - STRUCTURAL_SYSTEMS: Specific structural elements and their logic
        - MATERIALS_INDICATED: Materials that appear to be specified or suggested
        - ARCHITECTURAL_FEATURES: Notable design elements, details, or characteristics
        - ENVIRONMENTAL_STRATEGIES: Passive design, daylighting, ventilation strategies visible
        - LANDSCAPE_INTEGRATION: How the design relates to site and landscape
        - ACCESSIBILITY_FEATURES: Universal design elements visible

        STEP 4 - DESIGN INTENT ANALYSIS:
        Evaluate:
        - PRIMARY_DESIGN_CONCEPT: The main organizing idea or parti diagram
        - FUNCTIONAL_ORGANIZATION: How the design serves its intended purpose effectively
        - EXPERIENTIAL_QUALITIES: What it would feel like to inhabit and use these spaces
        - CULTURAL_CONTEXTUAL_ELEMENTS: Cultural, historical, or contextual references
        - INNOVATION_CREATIVITY: Unique or creative aspects of the design approach

        STEP 5 - TECHNICAL OBSERVATIONS:
        Assess:
        - CONSTRUCTION_IMPLICATIONS: Buildability, complexity, and construction considerations
        - CODE_COMPLIANCE_CONSIDERATIONS: Accessibility, egress, safety, zoning observations
        - SUSTAINABILITY_FEATURES: Environmental design aspects and performance strategies
        - STRUCTURAL_LOGIC: How the structural system appears to work and its efficiency
        - SYSTEMS_INTEGRATION: Mechanical, electrical, plumbing considerations visible

        STEP 6 - CRITIQUE AND SUGGESTIONS:
        Provide:
        - STRENGTHS: Specific aspects that work well and why they're effective
        - AREAS_FOR_DEVELOPMENT: Specific aspects that could be improved with actionable suggestions
        - QUESTIONS_TO_EXPLORE: Thoughtful design questions this work raises
        - NEXT_STEPS_SUGGESTIONS: Specific recommended design development steps
        - ALTERNATIVE_APPROACHES: Other ways to address the same design challenges

        STEP 7 - CONTEXTUAL RESPONSE:
        Generate a thoughtful, conversational 4-5 sentence response that:
        - Demonstrates deep understanding of what the user has shared
        - References specific elements you can see
        - Acknowledges their design thinking
        - Shows how this relates to their broader design goals
        - Sounds like a knowledgeable colleague who has carefully studied their work
        - Is specific about observations rather than generic
        - Makes the user feel understood and supported

        FORMAT: Use clear section headers. Be highly specific and reference actual elements you can see in the image. Avoid generic statements.
        """

        if context:
            prompt += f"\n\nPROJECT CONTEXT: {context}\nRelate your analysis to this specific context and provide phase-appropriate guidance."

        return prompt

    async def get_detailed_image_understanding(self, image_path: str, context: str = "") -> Dict[str, Any]:
        """Get detailed image understanding with enhanced contextual response"""
        try:
            # Encode image
            base64_image = self.encode_image(image_path)

            # Create enhanced analysis prompt
            analysis_prompt = self._create_comprehensive_prompt(context)

            print("📤 Sending enhanced comprehensive analysis request to GPT-4V...")

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

            # Get the raw analysis
            raw_analysis = response.choices[0].message.content

            # Structure the analysis and extract chat summary
            structured_analysis = self._structure_enhanced_analysis(raw_analysis, image_path, context)

            print(f"✅ Enhanced image understanding complete - {len(structured_analysis.get('chat_summary', ''))} chars in chat summary")

            return structured_analysis

        except Exception as e:
            print(f"❌ Error in enhanced image understanding: {e}")
            return {
                "error": f"Enhanced analysis failed: {str(e)}",
                "chat_summary": f"I can see you've uploaded an architectural image. While I had some difficulty with the detailed analysis, I can tell this appears to be an important part of your design process. Let's discuss what you're working on and how I can help you develop this further.",
                "timestamp": datetime.now().isoformat()
            }

    def generate_contextual_response(self, analysis_data: Dict[str, Any], user_message: str = "") -> str:
        """Generate a comprehensive contextual response that includes all 7-step analysis information"""

        # Extract the base contextual response from analysis
        base_response = analysis_data.get('chat_summary', 'Image analysis completed.')

        # Build comprehensive analysis description for the orchestrator
        comprehensive_description = self._build_comprehensive_description(analysis_data)

        # If there's a user message, create enhanced response
        if user_message.strip():
            # Extract key insights from analysis for context
            strengths = analysis_data.get('critique_and_suggestions', {}).get('strengths', [])
            suggestions = analysis_data.get('critique_and_suggestions', {}).get('next_steps_suggestions', [])

            enhanced_response = f"{base_response}\n\nRegarding your message: \"{user_message[:100]}{'...' if len(user_message) > 100 else ''}\", I can see how this relates to what you've shown in your design. "

            # Add specific insights if available
            if strengths and isinstance(strengths, list) and strengths:
                enhanced_response += f"The {strengths[0].lower()} you've demonstrated supports this direction. "

            # Add next steps if available
            if suggestions and isinstance(suggestions, list) and suggestions:
                enhanced_response += f"Moving forward, I'd suggest {suggestions[0].lower()}."

            # Append comprehensive analysis for orchestrator
            enhanced_response += f"\n\n{comprehensive_description}"

            return enhanced_response

        # Return base response with comprehensive analysis
        return f"{base_response}\n\n{comprehensive_description}"

    def _build_comprehensive_description(self, analysis_data: Dict[str, Any]) -> str:
        """Build a comprehensive natural language description of the 7-step analysis for the orchestrator"""

        description_parts = []

        # Add header to identify this as detailed image analysis
        description_parts.append("DETAILED IMAGE ANALYSIS FROM UPLOADED ARCHITECTURAL DRAWING:")

        # 1. Image Classification
        classification = analysis_data.get('classification', {})
        if classification:
            image_type = classification.get('image_type', 'architectural drawing')
            drawing_style = classification.get('drawing_style', 'unknown style')
            development_level = classification.get('development_level', 'unknown level')
            description_parts.append(f"This is a {image_type} in {drawing_style} at {development_level} of development.")

        # 2. Spatial Analysis
        spatial_analysis = analysis_data.get('spatial_analysis', {})
        if spatial_analysis:
            primary_spaces = spatial_analysis.get('primary_spaces', '')
            circulation = spatial_analysis.get('circulation_patterns', '')
            hierarchy = spatial_analysis.get('spatial_hierarchy', '')

            if primary_spaces:
                description_parts.append(f"The primary spaces include: {primary_spaces}")
            if circulation:
                description_parts.append(f"Circulation patterns show: {circulation}")
            if hierarchy:
                description_parts.append(f"Spatial hierarchy demonstrates: {hierarchy}")

        # 3. Design Elements
        design_elements = analysis_data.get('design_elements', {})
        if design_elements:
            structural = design_elements.get('structural_systems', '')
            materials = design_elements.get('materials_indicated', '')
            features = design_elements.get('architectural_features', '')

            if structural:
                description_parts.append(f"Structural approach: {structural}")
            if materials:
                description_parts.append(f"Materials indicated: {materials}")
            if features:
                description_parts.append(f"Notable architectural features: {features}")

        # 4. Design Intent
        design_intent = analysis_data.get('design_intent', {})
        if design_intent:
            concept = design_intent.get('primary_concept', '')
            organization = design_intent.get('functional_organization', '')
            experience = design_intent.get('experiential_qualities', '')

            if concept:
                description_parts.append(f"Primary design concept: {concept}")
            if organization:
                description_parts.append(f"Functional organization: {organization}")
            if experience:
                description_parts.append(f"Intended experience: {experience}")

        # 5. Technical Observations
        technical = analysis_data.get('technical_observations', {})
        if technical:
            construction = technical.get('construction_implications', '')
            sustainability = technical.get('sustainability_features', '')

            if construction:
                description_parts.append(f"Construction considerations: {construction}")
            if sustainability:
                description_parts.append(f"Sustainability aspects: {sustainability}")

        # 6. Critique and Suggestions
        critique = analysis_data.get('critique_and_suggestions', {})
        if critique:
            strengths = critique.get('strengths', [])
            areas_for_development = critique.get('areas_for_development', [])
            next_steps = critique.get('next_steps_suggestions', [])

            if strengths and isinstance(strengths, list):
                description_parts.append(f"Design strengths: {', '.join(strengths[:3])}")
            if areas_for_development and isinstance(areas_for_development, list):
                description_parts.append(f"Areas for development: {', '.join(areas_for_development[:3])}")
            if next_steps and isinstance(next_steps, list):
                description_parts.append(f"Suggested next steps: {', '.join(next_steps[:3])}")

        # 7. Confidence and Summary
        confidence = analysis_data.get('confidence_score', 0.7)
        description_parts.append(f"Analysis confidence: {confidence:.1f}/1.0")

        return " ".join(description_parts)

    def _structure_enhanced_analysis(self, raw_analysis: str, image_path: str, context: str = "") -> Dict[str, Any]:
        """Structure the enhanced analysis into organized categories with chat summary"""

        structured = {
            "raw_analysis": raw_analysis,
            "image_path": image_path,
            "context": context,
            "timestamp": datetime.now().isoformat(),
            "classification": self._extract_classification(raw_analysis),
            "spatial_analysis": self._extract_spatial_analysis(raw_analysis),
            "design_elements": self._extract_design_elements(raw_analysis),
            "design_intent": self._extract_design_intent(raw_analysis),
            "technical_observations": self._extract_technical_observations(raw_analysis),
            "critique_and_suggestions": self._extract_critique_suggestions(raw_analysis),
            "chat_summary": self._extract_contextual_response(raw_analysis),
            "confidence_score": self._calculate_confidence(raw_analysis)
        }

        return structured

    def _extract_contextual_response(self, raw_analysis: str) -> str:
        """Extract the contextual response from the analysis"""
        # Look for the contextual response section
        lines = raw_analysis.split('\n')
        contextual_section = False
        contextual_lines = []

        for line in lines:
            if 'CONTEXTUAL RESPONSE' in line.upper() or 'STEP 7' in line:
                contextual_section = True
                continue
            elif contextual_section and line.strip():
                if line.startswith('STEP ') or line.startswith('##'):
                    break
                contextual_lines.append(line.strip())

        if contextual_lines:
            return ' '.join(contextual_lines)

        # Fallback: look for any conversational summary
        for line in lines:
            if any(word in line.lower() for word in ['can see', 'shows', 'demonstrates', 'your design']):
                if len(line.strip()) > 50:  # Ensure it's substantial
                    return line.strip()

        # Final fallback
        return "I can see you've shared an architectural drawing that shows thoughtful consideration of spatial relationships and design intent. This appears to be a meaningful part of your design development process."

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

        # Check cache first if enabled
        if self.use_cache and self.cache:
            cache_key = f"detailed_{context}"
            cached_result = self.cache.get_cached_analysis(image_path)
            if cached_result and cache_key in cached_result:
                print("⚡ Using cached detailed understanding")
                return cached_result[cache_key]

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

            result = {
                "detailed_analysis": detailed_understanding,
                "key_insights": key_insights,
                "chat_summary": self._create_chat_summary(key_insights),
                "timestamp": datetime.now().isoformat(),
                "confidence": self._calculate_understanding_confidence(detailed_understanding)
            }

            # Cache the result if caching is enabled
            if self.use_cache and self.cache:
                cache_key = f"detailed_{context}"
                cached_result = self.cache.get_cached_analysis(image_path) or {}
                cached_result[cache_key] = result
                self.cache.cache_analysis(image_path, cached_result)

            return result

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

    def _extract_spatial_analysis(self, raw_analysis: str) -> Dict[str, Any]:
        """Extract spatial analysis from raw analysis"""
        spatial_data = {}
        lines = raw_analysis.split('\n')

        # Look for spatial analysis section
        in_spatial_section = False
        for line in lines:
            if 'SPATIAL ANALYSIS' in line.upper() or 'STEP 2' in line:
                in_spatial_section = True
                continue
            elif in_spatial_section and line.strip():
                if line.startswith('STEP ') or line.startswith('##'):
                    break
                if 'PRIMARY_SPACES' in line.upper():
                    spatial_data['primary_spaces'] = line.split(':', 1)[-1].strip()
                elif 'CIRCULATION' in line.upper():
                    spatial_data['circulation_patterns'] = line.split(':', 1)[-1].strip()
                elif 'HIERARCHY' in line.upper():
                    spatial_data['spatial_hierarchy'] = line.split(':', 1)[-1].strip()
                elif 'INDOOR_OUTDOOR' in line.upper():
                    spatial_data['indoor_outdoor_relationships'] = line.split(':', 1)[-1].strip()

        return spatial_data

    def _extract_design_elements(self, raw_analysis: str) -> Dict[str, Any]:
        """Extract design elements from raw analysis"""
        elements_data = {}
        lines = raw_analysis.split('\n')

        # Look for design elements section
        in_elements_section = False
        for line in lines:
            if 'DESIGN ELEMENTS' in line.upper() or 'STEP 3' in line:
                in_elements_section = True
                continue
            elif in_elements_section and line.strip():
                if line.startswith('STEP ') or line.startswith('##'):
                    break
                if 'STRUCTURAL' in line.upper():
                    elements_data['structural_systems'] = line.split(':', 1)[-1].strip()
                elif 'MATERIALS' in line.upper():
                    elements_data['materials_indicated'] = line.split(':', 1)[-1].strip()
                elif 'ARCHITECTURAL_FEATURES' in line.upper():
                    elements_data['architectural_features'] = line.split(':', 1)[-1].strip()

        return elements_data

    def _extract_design_intent(self, raw_analysis: str) -> Dict[str, Any]:
        """Extract design intent analysis from raw analysis"""
        intent_data = {}
        lines = raw_analysis.split('\n')

        # Look for design intent section
        in_intent_section = False
        for line in lines:
            if 'DESIGN INTENT' in line.upper() or 'STEP 4' in line:
                in_intent_section = True
                continue
            elif in_intent_section and line.strip():
                if line.startswith('STEP ') or line.startswith('##'):
                    break
                if 'PRIMARY_DESIGN_CONCEPT' in line.upper():
                    intent_data['primary_concept'] = line.split(':', 1)[-1].strip()
                elif 'FUNCTIONAL_ORGANIZATION' in line.upper():
                    intent_data['functional_organization'] = line.split(':', 1)[-1].strip()
                elif 'EXPERIENTIAL' in line.upper():
                    intent_data['experiential_qualities'] = line.split(':', 1)[-1].strip()

        return intent_data

    def _extract_technical_observations(self, raw_analysis: str) -> Dict[str, Any]:
        """Extract technical observations from raw analysis"""
        technical_data = {}
        lines = raw_analysis.split('\n')

        # Look for technical observations section
        in_technical_section = False
        for line in lines:
            if 'TECHNICAL OBSERVATIONS' in line.upper() or 'STEP 5' in line:
                in_technical_section = True
                continue
            elif in_technical_section and line.strip():
                if line.startswith('STEP ') or line.startswith('##'):
                    break
                if 'CONSTRUCTION' in line.upper():
                    technical_data['construction_implications'] = line.split(':', 1)[-1].strip()
                elif 'CODE_COMPLIANCE' in line.upper():
                    technical_data['code_compliance'] = line.split(':', 1)[-1].strip()
                elif 'SUSTAINABILITY' in line.upper():
                    technical_data['sustainability_features'] = line.split(':', 1)[-1].strip()

        return technical_data

    def _extract_critique_suggestions(self, raw_analysis: str) -> Dict[str, Any]:
        """Extract critique and suggestions from raw analysis"""
        critique_data = {}
        lines = raw_analysis.split('\n')

        # Look for critique section
        in_critique_section = False
        for line in lines:
            if 'CRITIQUE' in line.upper() or 'STEP 6' in line:
                in_critique_section = True
                continue
            elif in_critique_section and line.strip():
                if line.startswith('STEP ') or line.startswith('##'):
                    break
                if 'STRENGTHS' in line.upper():
                    critique_data['strengths'] = [line.split(':', 1)[-1].strip()]
                elif 'AREAS_FOR_DEVELOPMENT' in line.upper():
                    critique_data['areas_for_development'] = [line.split(':', 1)[-1].strip()]
                elif 'NEXT_STEPS' in line.upper():
                    critique_data['next_steps_suggestions'] = [line.split(':', 1)[-1].strip()]

        return critique_data

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

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics if caching is enabled."""
        if self.use_cache and self.cache:
            return self.cache.get_cache_stats()
        else:
            return {"caching": "disabled"}

    def clear_cache(self):
        """Clear the image analysis cache if caching is enabled."""
        if self.use_cache and self.cache:
            self.cache.clear_cache()
            print("🗑️ Vision analyzer cache cleared")
        else:
            print("⚠️ Caching is disabled, nothing to clear")
