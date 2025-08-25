# vision/sketch_analyzer.py
import base64
import cv2
import numpy as np
from PIL import Image
from openai import OpenAI
import os
import sys
import json
from typing import Dict, Any, List

# Add utils to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'utils'))

try:
    from secrets_manager import get_openai_api_key
except ImportError:
    # Fallback if secrets_manager is not available
    def get_openai_api_key() -> str:
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass
        return os.getenv("OPENAI_API_KEY", "")

class SketchAnalyzer:
    def __init__(self, domain="architecture"):
        self.client = OpenAI(api_key=get_openai_api_key())
        self.domain = domain
        
        # Enhanced domain-specific analysis prompts with structured classification
        self.domain_prompts = {
            "architecture": """
                You are an expert architectural analyst with advanced visual processing capabilities. Provide a comprehensive, systematic analysis of this architectural image.

                STEP 1 - IMAGE CLASSIFICATION & TYPE IDENTIFICATION:
                First, systematically identify:
                - IMAGE TYPE: Is this a floor plan, elevation, section, axonometric, perspective, 3D rendering, sketch, photograph, or technical drawing?
                - DRAWING MEDIUM: Hand-drawn, digital CAD, mixed media, photograph, or rendering?
                - PERSPECTIVE/VIEW: Plan view, elevation view, section cut, isometric, perspective, or other?
                - SCALE/DETAIL LEVEL: Conceptual sketch, schematic design, design development, or construction document level?
                - DRAWING CONVENTIONS: Line weights, hatching patterns, symbols, dimensions, annotations used?

                STEP 2 - VISUAL ELEMENTS ANALYSIS:
                Systematically identify and describe:
                - SHAPES & GEOMETRY: What geometric forms, shapes, and spatial configurations are present?
                - COLORS & MATERIALS: What colors, textures, and material representations are shown?
                - SPATIAL ORGANIZATION: How are spaces arranged and connected?
                - STRUCTURAL ELEMENTS: Walls, columns, beams, openings, stairs, etc.
                - CIRCULATION PATTERNS: Movement paths, entrances, connections between spaces?

                2. SPATIAL ORGANIZATION & LAYOUT:
                   - Describe the exact arrangement of spaces - how many rooms/areas?
                   - What is the overall organizational strategy (linear, clustered, courtyard, etc.)?
                   - How are public, semi-public, and private spaces arranged?
                   - What are the specific dimensions or proportional relationships you can observe?
                   - Describe the hierarchy of spaces from largest to smallest

                3. CIRCULATION & MOVEMENT:
                   - Trace the primary circulation paths - where do they lead?
                   - Are there secondary or service circulation routes?
                   - How do vertical circulation elements (stairs, elevators, ramps) connect levels?
                   - What is the sequence of spaces a person would experience?
                   - Are there clear wayfinding elements or visual connections?

                4. ACCESS POINTS & OPENINGS:
                   - Count and describe all doors, windows, and openings
                   - Where is the main entrance? Are there secondary entrances?
                   - How do openings relate to interior and exterior spaces?
                   - What is the rhythm and pattern of fenestration?
                   - Are there any special opening types (curtain walls, skylights, etc.)?

                5. STRUCTURAL & BUILDING SYSTEMS:
                   - Identify structural elements: walls (load-bearing vs. partition), columns, beams
                   - What structural system is implied (post-and-beam, bearing wall, etc.)?
                   - Are there any mechanical, electrical, or plumbing elements visible?
                   - How thick are walls? What might this suggest about materials or structure?

                6. SITE RELATIONSHIP & CONTEXT:
                   - How does the building relate to site boundaries, topography, or context?
                   - Are there outdoor spaces, courtyards, or landscape elements?
                   - What is the building's orientation and how might this affect daylighting?
                   - Are there any site-specific design responses visible?

                7. MATERIALS & CONSTRUCTION DETAILS:
                   - What materials are indicated through drawing conventions or notes?
                   - Are there any construction details or technical elements shown?
                   - What does the drawing suggest about the building's materiality?

                8. DESIGN QUALITY & ARCHITECTURAL PRINCIPLES:
                   - Evaluate proportion, scale, and hierarchy
                   - Assess functionality and programmatic organization
                   - Comment on spatial quality and experiential aspects
                   - Identify any innovative or noteworthy design moves

                9. SPECIFIC OBSERVATIONS:
                   - Note any text, dimensions, or annotations
                   - Identify any symbols, furniture, or equipment shown
                   - Describe any unique or unusual elements
                   - Comment on the overall design intent or concept

                10. DESIGN EVALUATION & RECOMMENDATIONS:
                    - STRENGTHS: What works well in this design and why?
                    - IMPROVEMENT OPPORTUNITIES: Specific, actionable suggestions for enhancement
                    - FUNCTIONAL ASSESSMENT: How well does it serve intended uses and users?
                    - ACCESSIBILITY CONSIDERATIONS: Universal design and inclusive access
                    - SUSTAINABILITY POTENTIAL: Environmental design opportunities
                    - TECHNICAL DEVELOPMENT: Areas needing further technical resolution

                RESPONSE FORMAT:
                Structure your analysis with clear headers for each section. Use bullet points for specific observations.
                Be precise and avoid generic statements. Base all observations on what is actually visible in the image.
                Provide both technical analysis and experiential/qualitative assessment.
                Include specific recommendations for improvement where appropriate.
            """,
            
            "game_design": """
                You are an expert game design analyst. Provide a comprehensive, detailed analysis of this game design sketch/level layout/concept art. Be extremely specific about what you observe.

                ANALYZE IN DETAIL:

                1. VISUAL REPRESENTATION & STYLE:
                   - What type of game design document is this (level layout, concept art, UI mockup, character design)?
                   - What art style or visual approach is used?
                   - What perspective or view is shown (top-down, side-scrolling, isometric, 3D)?
                   - Describe the visual elements, colors, and artistic choices

                2. LEVEL DESIGN & SPATIAL ORGANIZATION:
                   - Map out the exact layout - what are the distinct areas or zones?
                   - How is the space organized for gameplay flow?
                   - What is the scale and scope of the playable area?
                   - Are there different gameplay zones with distinct functions?

                3. PLAYER MOVEMENT & NAVIGATION:
                   - Trace all possible player paths and routes
                   - Are there multiple ways to traverse the space?
                   - What movement mechanics are implied (walking, jumping, climbing, flying)?
                   - How does the layout guide or restrict player movement?

                4. GAMEPLAY ELEMENTS & MECHANICS:
                   - Identify all interactive elements, objects, or mechanics visible
                   - What obstacles, challenges, or puzzles are present?
                   - Are there collectibles, power-ups, or special items?
                   - What combat or interaction scenarios are suggested?

                5. OBJECTIVES & GOALS:
                   - What are the apparent objectives or win conditions?
                   - Are there multiple goals or a progression of objectives?
                   - How are goals communicated visually?

                6. DIFFICULTY & PACING:
                   - How does the design suggest difficulty progression?
                   - Are there safe zones, checkpoints, or rest areas?
                   - What is the pacing of challenges and rewards?

                7. PLAYER PSYCHOLOGY & ENGAGEMENT:
                   - What elements would create player interest or excitement?
                   - How does the design encourage exploration or experimentation?
                   - Are there surprise elements or hidden areas?

                8. TECHNICAL CONSIDERATIONS:
                   - What technical constraints or requirements are implied?
                   - How might this design be implemented in a game engine?
                   - Are there any performance or technical challenges suggested?

                9. NARRATIVE & THEME:
                   - What story or thematic elements are present?
                   - How does the visual design support the game's narrative?
                   - What mood or atmosphere is created?

                10. DESIGN STRENGTHS & OPPORTUNITIES:
                    - What gameplay elements work particularly well?
                    - What could enhance the player experience?
                    - Are there any design issues or areas for improvement?

                PROVIDE A RICH, DETAILED DESCRIPTION that captures both the technical gameplay aspects and the experiential qualities of the design. Use specific game design terminology and be as descriptive as possible about what you actually see.
            """
        }
    
    def encode_image(self, image_path: str) -> str:
        """Convert image to base64 for OpenAI API"""
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            raise ValueError(f"Could not encode image {image_path}: {str(e)}")
    
    def preprocess_image(self, image_path: str) -> str:
        """Enhance sketch for better analysis"""
        try:
            # Load image
            img = cv2.imread(image_path)
            if img is None:
                print(f"⚠️ Could not load image: {image_path}, using original")
                return image_path
            
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Enhance contrast for better line detection
            enhanced = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            # Save enhanced version
            base_name = os.path.splitext(image_path)[0]
            enhanced_path = f"{base_name}_enhanced.jpg"
            cv2.imwrite(enhanced_path, enhanced)
            
            print(f"✅ Image preprocessed: {enhanced_path}")
            return enhanced_path
            
        except Exception as e:
            print(f"⚠️ Image preprocessing failed: {e}, using original")
            return image_path  # Return original if preprocessing fails
    
    async def analyze_sketch(self, image_path: str, context: str = "") -> Dict[str, Any]:
        """Main analysis function using GPT-4V"""
        
        print(f"🔍 Analyzing image: {image_path}")
        
        try:
            # Preprocess image for better analysis
            processed_path = self.preprocess_image(image_path)
            
            # Encode image
            base64_image = self.encode_image(processed_path)
            
            # Get domain-specific prompt
            analysis_prompt = self.domain_prompts.get(self.domain, self.domain_prompts["architecture"])
            
            if context:
                analysis_prompt += f"\n\nPROJECT CONTEXT: {context}"
                analysis_prompt += "\n\nPlease relate your analysis to this specific project context."
            
            print("📤 Sending to GPT-4V...")
            
            # Call GPT-4O
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
                max_tokens=1500,
                temperature=0.3
            )
            
            analysis_text = response.choices[0].message.content
            print("✅ GPT-4V analysis complete")
            
            # Structure the analysis
            structured_analysis = {
                "raw_analysis": analysis_text,
                "identified_elements": self.extract_elements(analysis_text),
                "design_strengths": self.extract_strengths(analysis_text),
                "improvement_opportunities": self.extract_opportunities(analysis_text),
                "accessibility_notes": self.extract_accessibility_info(analysis_text),
                "spatial_relationships": self.extract_spatial_info(analysis_text),
                "confidence_score": self.estimate_confidence(analysis_text),
                "domain": self.domain
            }
            
            print(f"📊 Analysis structured. Confidence: {structured_analysis['confidence_score']}")
            return structured_analysis
            
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            return {
                "error": str(e),
                "raw_analysis": "Could not analyze image due to error",
                "confidence_score": 0.0,
                "domain": self.domain
            }
    
    def extract_elements(self, analysis: str) -> List[str]:
        """Extract design elements mentioned in analysis"""
        elements = []
        
        # Architecture elements
        arch_elements = ["wall", "door", "window", "room", "space", "entrance", 
                        "stair", "corridor", "bathroom", "kitchen", "bedroom",
                        "courtyard", "lobby", "office", "hall", "storage"]
        
        # Game design elements  
        game_elements = ["platform", "obstacle", "enemy", "collectible", "checkpoint",
                        "level", "path", "goal", "spawn", "exit", "power-up", "trap"]
        
        element_list = arch_elements if self.domain == "architecture" else game_elements
        
        analysis_lower = analysis.lower()
        for element in element_list:
            if element.lower() in analysis_lower:
                elements.append(element)
        
        return list(set(elements))  # Remove duplicates
    
    def extract_strengths(self, analysis: str) -> List[str]:
        """Extract positive aspects mentioned"""
        positive_keywords = ["good", "effective", "strong", "clear", "well", 
                           "successful", "excellent", "clever", "smart", "logical",
                           "appropriate", "efficient", "thoughtful"]
        
        sentences = [s.strip() for s in analysis.split('.') if s.strip()]
        strengths = []
        
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in positive_keywords):
                if len(sentence) > 10:  # Filter out very short sentences
                    strengths.append(sentence)
        
        return strengths[:4]  # Return top 4 strengths
    
    def extract_opportunities(self, analysis: str) -> List[str]:
        """Extract improvement suggestions"""
        improvement_keywords = ["could", "might", "consider", "improve", "add", 
                              "lacks", "missing", "needs", "should", "recommend",
                              "suggest", "enhance", "better", "reconsider"]
        
        sentences = [s.strip() for s in analysis.split('.') if s.strip()]
        opportunities = []
        
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in improvement_keywords):
                if len(sentence) > 10:  # Filter out very short sentences
                    opportunities.append(sentence)
        
        return opportunities[:4]  # Return top 4 opportunities
    
    def extract_accessibility_info(self, analysis: str) -> List[str]:
        """Extract accessibility-related observations"""
        accessibility_keywords = ["accessibility", "wheelchair", "ramp", "accessible", 
                                "barrier", "ada", "disability", "universal design",
                                "mobility", "step", "elevation", "grade"]
        
        sentences = [s.strip() for s in analysis.split('.') if s.strip()]
        accessibility_notes = []
        
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in accessibility_keywords):
                if len(sentence) > 10:
                    accessibility_notes.append(sentence)
        
        return accessibility_notes
    
    def extract_spatial_info(self, analysis: str) -> List[str]:
        """Extract spatial relationship observations"""
        spatial_keywords = ["relationship", "connection", "adjacent", "nearby",
                           "circulation", "flow", "sequence", "hierarchy",
                           "proportion", "scale", "organization"]
        
        sentences = [s.strip() for s in analysis.split('.') if s.strip()]
        spatial_notes = []
        
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in spatial_keywords):
                if len(sentence) > 10:
                    spatial_notes.append(sentence)
        
        return spatial_notes[:3]  # Return top 3 spatial observations
    
    def estimate_confidence(self, analysis: str) -> float:
        """Estimate confidence in analysis quality"""
        # Simple heuristic based on analysis length and detail
        word_count = len(analysis.split())
        
        # Look for specific architectural/design terminology
        detail_keywords = ["specifically", "particular", "notice", "observe", "see",
                          "appears", "suggests", "indicates", "demonstrates"]
        detail_count = sum(1 for keyword in detail_keywords if keyword in analysis.lower())
        
        # Look for structured analysis
        structure_keywords = ["first", "second", "also", "however", "additionally",
                            "furthermore", "moreover", "in contrast"]
        structure_count = sum(1 for keyword in structure_keywords if keyword in analysis.lower())
        
        # Base confidence on multiple factors
        length_score = min(word_count / 300, 1.0)  # 300 words = full score
        detail_score = min(detail_count / 5, 1.0)   # 5 detail words = full score
        structure_score = min(structure_count / 3, 1.0)  # 3 structure words = full score
        
        confidence = (length_score * 0.5 + detail_score * 0.3 + structure_score * 0.2)
        return round(max(0.1, min(1.0, confidence)), 2)

    async def classify_and_analyze_image(self, image_path: str, context: str = "") -> Dict[str, Any]:
        """Comprehensive image classification and analysis with structured output"""

        print(f"🔍 Performing comprehensive image analysis: {image_path}")

        try:
            # Preprocess image for better analysis
            processed_path = self.preprocess_image(image_path)

            # Encode image
            base64_image = self.encode_image(processed_path)

            # Create comprehensive classification and analysis prompt
            classification_prompt = f"""
            You are an expert architectural visual analyst. Perform a comprehensive, systematic analysis of this image.

            STEP 1 - IMAGE CLASSIFICATION (Provide specific answers):
            - IMAGE_TYPE: [floor_plan | elevation | section | axonometric | perspective | 3d_rendering | sketch | photograph | technical_drawing | other]
            - DRAWING_MEDIUM: [hand_drawn | digital_cad | mixed_media | photograph | rendering | other]
            - PERSPECTIVE_VIEW: [plan_view | elevation_view | section_cut | isometric | perspective | bird_eye | other]
            - DETAIL_LEVEL: [conceptual_sketch | schematic_design | design_development | construction_document | presentation_drawing]
            - DRAWING_STYLE: [architectural_technical | artistic_sketch | presentation_quality | working_drawing | conceptual]

            STEP 2 - VISUAL ELEMENTS EXTRACTION:
            - DOMINANT_SHAPES: List the main geometric forms and shapes visible
            - COLOR_PALETTE: Describe colors used (if any) and their significance
            - LINE_QUALITIES: Describe line weights, styles, and drawing techniques
            - SPATIAL_ORGANIZATION: How spaces/elements are arranged and connected
            - SCALE_INDICATORS: Any dimensions, scale bars, or size references

            STEP 3 - ARCHITECTURAL CONTENT ANALYSIS:
            - BUILDING_ELEMENTS: List specific architectural components (walls, doors, windows, stairs, etc.)
            - SPATIAL_HIERARCHY: Describe the organization and relationship of spaces
            - CIRCULATION_PATTERNS: Movement paths and connections
            - STRUCTURAL_SYSTEMS: Visible structural elements and approaches
            - FUNCTIONAL_ZONES: Different program areas and their relationships

            STEP 4 - TECHNICAL ASSESSMENT:
            - DRAWING_COMPLETENESS: How developed and detailed is the drawing?
            - TECHNICAL_ACCURACY: Proper use of conventions and standards?
            - CLARITY_COMMUNICATION: How well does it convey design intent?
            - ANNOTATIONS_DIMENSIONS: Text, labels, measurements present?

            STEP 5 - DESIGN EVALUATION:
            - DESIGN_STRENGTHS: What works well and why? (be specific)
            - IMPROVEMENT_AREAS: Specific suggestions for enhancement
            - FUNCTIONAL_ASSESSMENT: How well does it serve intended purposes?
            - ACCESSIBILITY_NOTES: Universal design considerations
            - SUSTAINABILITY_OPPORTUNITIES: Environmental design potential

            FORMAT: Provide your analysis in clear sections with specific, actionable observations. Avoid generic statements.
            """

            if context:
                classification_prompt += f"\n\nPROJECT CONTEXT: {context}\nPlease relate your analysis to this specific project context."

            print("📤 Sending comprehensive analysis request to GPT-4V...")

            # Call GPT-4O for comprehensive analysis
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": classification_prompt},
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
                max_tokens=2500,  # Increased for comprehensive analysis
                temperature=0.2   # Lower temperature for more factual analysis
            )

            comprehensive_analysis = response.choices[0].message.content
            print("✅ Comprehensive image analysis complete")

            # Structure the analysis into categories
            structured_result = {
                "raw_comprehensive_analysis": comprehensive_analysis,
                "image_classification": self._extract_classification_data(comprehensive_analysis),
                "visual_elements": self._extract_visual_elements(comprehensive_analysis),
                "architectural_content": self._extract_architectural_content(comprehensive_analysis),
                "technical_assessment": self._extract_technical_assessment(comprehensive_analysis),
                "design_evaluation": self._extract_design_evaluation(comprehensive_analysis),
                "confidence_score": self.estimate_confidence(comprehensive_analysis),
                "analysis_timestamp": datetime.now().isoformat(),
                "domain": self.domain
            }

            return structured_result

        except Exception as e:
            print(f"❌ Error in comprehensive image analysis: {e}")
            return {
                "error": f"Comprehensive analysis failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }

    async def generate_detailed_description(self, image_path: str, context: str = "") -> str:
        """Generate a detailed description of the image for system understanding"""

        print(f"🔍 Generating detailed description for: {image_path}")

        try:
            # Preprocess image for better analysis
            processed_path = self.preprocess_image(image_path)

            # Encode image
            base64_image = self.encode_image(processed_path)

            # Create a prompt specifically for detailed description
            description_prompt = f"""
            You are an expert visual analyst. Your task is to provide an extremely detailed, comprehensive description of this image that will help an AI system understand exactly what is shown.

            PROVIDE A DETAILED DESCRIPTION INCLUDING:

            1. OVERALL COMPOSITION:
               - What type of image is this? (sketch, photograph, digital rendering, technical drawing, etc.)
               - What is the main subject or focus?
               - What is the viewing angle or perspective?
               - Describe the overall layout and composition

            2. SPECIFIC VISUAL ELEMENTS:
               - List and describe every visible object, structure, or element
               - Note colors, textures, materials, and finishes
               - Describe shapes, forms, and geometric relationships
               - Identify any text, labels, dimensions, or annotations

            3. SPATIAL RELATIONSHIPS:
               - How are elements positioned relative to each other?
               - What are the proportional relationships?
               - Describe depth, scale, and dimensional qualities
               - Note any perspective or viewing angle effects

            4. TECHNICAL DETAILS:
               - Any construction or technical details visible
               - Drawing conventions, line weights, or symbols used
               - Level of detail and precision shown
               - Any measurements, scales, or technical annotations

            5. CONTEXT AND SETTING:
               - Environmental context or background elements
               - Site conditions, landscape, or surrounding context
               - Lighting conditions and shadows
               - Any contextual clues about location or setting

            6. DESIGN INTENT AND CONCEPT:
               - What design ideas or concepts are being communicated?
               - What is the apparent purpose or function?
               - Any innovative or notable design features
               - Overall design approach or style

            {f"PROJECT CONTEXT: {context}" if context else ""}

            Write a comprehensive, detailed description that captures every important visual aspect. Use specific, descriptive language that would allow someone who hasn't seen the image to understand exactly what is shown. Focus on observable facts and details rather than interpretations.
            """

            print("📤 Sending to GPT-4V for detailed description...")

            # Call GPT-4O for detailed description
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": description_prompt},
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
                max_tokens=2000,  # Increased for detailed descriptions
                temperature=0.2   # Lower temperature for more factual descriptions
            )

            detailed_description = response.choices[0].message.content
            print("✅ Detailed description generated successfully")
            return detailed_description

        except Exception as e:
            print(f"❌ Error generating detailed description: {e}")
            return f"Error generating description: {str(e)}"

    def _extract_classification_data(self, analysis: str) -> Dict[str, str]:
        """Extract image classification data from comprehensive analysis"""
        classification = {}

        # Define classification patterns to look for
        patterns = {
            "image_type": ["IMAGE_TYPE:", "Type:", "Drawing type:"],
            "drawing_medium": ["DRAWING_MEDIUM:", "Medium:", "Drawing medium:"],
            "perspective_view": ["PERSPECTIVE_VIEW:", "View:", "Perspective:"],
            "detail_level": ["DETAIL_LEVEL:", "Detail level:", "Level of detail:"],
            "drawing_style": ["DRAWING_STYLE:", "Style:", "Drawing style:"]
        }

        analysis_lower = analysis.lower()

        for key, search_terms in patterns.items():
            for term in search_terms:
                term_lower = term.lower()
                if term_lower in analysis_lower:
                    # Find the line containing this term
                    lines = analysis.split('\n')
                    for line in lines:
                        if term_lower in line.lower():
                            # Extract the value after the term
                            parts = line.split(':')
                            if len(parts) > 1:
                                value = parts[1].strip().split()[0] if parts[1].strip() else "unknown"
                                classification[key] = value.replace('[', '').replace(']', '').replace('|', '')
                                break
                    break

        return classification

    def _extract_visual_elements(self, analysis: str) -> Dict[str, Any]:
        """Extract visual elements from comprehensive analysis"""
        visual_elements = {}

        # Look for visual element sections
        sections = {
            "dominant_shapes": ["DOMINANT_SHAPES:", "Shapes:", "Geometric forms:"],
            "color_palette": ["COLOR_PALETTE:", "Colors:", "Color scheme:"],
            "line_qualities": ["LINE_QUALITIES:", "Line quality:", "Drawing technique:"],
            "spatial_organization": ["SPATIAL_ORGANIZATION:", "Organization:", "Layout:"],
            "scale_indicators": ["SCALE_INDICATORS:", "Scale:", "Dimensions:"]
        }

        for key, search_terms in sections.items():
            for term in search_terms:
                if term.lower() in analysis.lower():
                    # Find and extract the relevant content
                    lines = analysis.split('\n')
                    for i, line in enumerate(lines):
                        if term.lower() in line.lower():
                            # Get the content after the term
                            content = line.split(':', 1)[1].strip() if ':' in line else ""
                            # Also check next few lines for continuation
                            for j in range(1, 3):
                                if i + j < len(lines) and lines[i + j].strip() and not any(s in lines[i + j] for s in ['STEP', ':', '-']):
                                    content += " " + lines[i + j].strip()
                            visual_elements[key] = content
                            break
                    break

        return visual_elements

    def _extract_architectural_content(self, analysis: str) -> Dict[str, Any]:
        """Extract architectural content from comprehensive analysis"""
        architectural_content = {}

        sections = {
            "building_elements": ["BUILDING_ELEMENTS:", "Elements:", "Components:"],
            "spatial_hierarchy": ["SPATIAL_HIERARCHY:", "Hierarchy:", "Space organization:"],
            "circulation_patterns": ["CIRCULATION_PATTERNS:", "Circulation:", "Movement:"],
            "structural_systems": ["STRUCTURAL_SYSTEMS:", "Structure:", "Structural elements:"],
            "functional_zones": ["FUNCTIONAL_ZONES:", "Functions:", "Program areas:"]
        }

        for key, search_terms in sections.items():
            for term in search_terms:
                if term.lower() in analysis.lower():
                    lines = analysis.split('\n')
                    for i, line in enumerate(lines):
                        if term.lower() in line.lower():
                            content = line.split(':', 1)[1].strip() if ':' in line else ""
                            # Check next few lines for continuation
                            for j in range(1, 4):
                                if i + j < len(lines) and lines[i + j].strip() and not any(s in lines[i + j] for s in ['STEP', ':']):
                                    content += " " + lines[i + j].strip()
                            architectural_content[key] = content
                            break
                    break

        return architectural_content

    def _extract_technical_assessment(self, analysis: str) -> Dict[str, str]:
        """Extract technical assessment from comprehensive analysis"""
        technical_assessment = {}

        sections = {
            "drawing_completeness": ["DRAWING_COMPLETENESS:", "Completeness:", "Development level:"],
            "technical_accuracy": ["TECHNICAL_ACCURACY:", "Accuracy:", "Technical quality:"],
            "clarity_communication": ["CLARITY_COMMUNICATION:", "Clarity:", "Communication:"],
            "annotations_dimensions": ["ANNOTATIONS_DIMENSIONS:", "Annotations:", "Labels:"]
        }

        for key, search_terms in sections.items():
            for term in search_terms:
                if term.lower() in analysis.lower():
                    lines = analysis.split('\n')
                    for i, line in enumerate(lines):
                        if term.lower() in line.lower():
                            content = line.split(':', 1)[1].strip() if ':' in line else ""
                            technical_assessment[key] = content
                            break
                    break

        return technical_assessment

    def _extract_design_evaluation(self, analysis: str) -> Dict[str, Any]:
        """Extract design evaluation from comprehensive analysis"""
        design_evaluation = {}

        sections = {
            "design_strengths": ["DESIGN_STRENGTHS:", "Strengths:", "What works well:"],
            "improvement_areas": ["IMPROVEMENT_AREAS:", "Improvements:", "Areas for improvement:"],
            "functional_assessment": ["FUNCTIONAL_ASSESSMENT:", "Functionality:", "Functional quality:"],
            "accessibility_notes": ["ACCESSIBILITY_NOTES:", "Accessibility:", "Universal design:"],
            "sustainability_opportunities": ["SUSTAINABILITY_OPPORTUNITIES:", "Sustainability:", "Environmental:"]
        }

        for key, search_terms in sections.items():
            for term in search_terms:
                if term.lower() in analysis.lower():
                    lines = analysis.split('\n')
                    for i, line in enumerate(lines):
                        if term.lower() in line.lower():
                            content = line.split(':', 1)[1].strip() if ':' in line else ""
                            # Check next few lines for continuation
                            for j in range(1, 5):
                                if i + j < len(lines) and lines[i + j].strip() and not any(s in lines[i + j] for s in ['STEP', ':']):
                                    content += " " + lines[i + j].strip()
                            design_evaluation[key] = content
                            break
                    break

        return design_evaluation