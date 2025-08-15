# vision/sketch_analyzer.py
import base64
import cv2
import numpy as np
from PIL import Image
from openai import OpenAI
import os
from dotenv import load_dotenv
import json
from typing import Dict, Any, List

load_dotenv()

class SketchAnalyzer:
    def __init__(self, domain="architecture"):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.domain = domain
        
        # Domain-specific analysis prompts - Enhanced for detailed analysis
        self.domain_prompts = {
            "architecture": """
                You are an expert architectural analyst. Provide a comprehensive, detailed analysis of this architectural drawing/sketch/plan. Be extremely specific and descriptive about what you observe.

                ANALYZE IN DETAIL:

                1. DRAWING TYPE & REPRESENTATION:
                   - Is this a plan view, section, elevation, axonometric, perspective, or sketch?
                   - What scale or level of detail is shown?
                   - Is it hand-drawn, digital, or mixed media?
                   - What drawing conventions are used (line weights, hatching, symbols)?

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

                10. AREAS FOR DEVELOPMENT:
                    - What aspects could be clarified or developed further?
                    - Are there any functional or design issues to address?
                    - What questions does this drawing raise about the design?

                PROVIDE A RICH, DETAILED DESCRIPTION that captures both the technical and experiential qualities of the design. Use specific architectural terminology and be as descriptive as possible about what you actually see in the image.
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