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
        
        # Domain-specific analysis prompts
        self.domain_prompts = {
            "architecture": """
                Analyze this architectural sketch/plan carefully. Look for:
                
                1. SPATIAL ORGANIZATION: How are rooms/spaces arranged? What's the overall layout strategy?
                2. CIRCULATION: How do people move through the space? Are there clear paths?
                3. ACCESS POINTS: Where are doors, windows, entrances? Are they logical?
                4. STRUCTURAL ELEMENTS: Can you identify walls, columns, stairs, structural systems?
                5. ACCESSIBILITY: Are there accessibility considerations visible? Any barriers?
                6. DESIGN STRENGTHS: What works well in this design?
                7. IMPROVEMENT OPPORTUNITIES: What could be enhanced or reconsidered?
                8. BUILDING SYSTEMS: Any evidence of lighting, ventilation, or other systems?
                
                Be specific about what you observe. Point out both positive aspects and areas for development.
                Focus on architectural principles like proportion, hierarchy, and functionality.
            """,
            
            "game_design": """
                Analyze this game design sketch/level layout. Look for:
                
                1. LEVEL LAYOUT: How is the space organized for gameplay?
                2. PLAYER PATHS: What routes can players take? Are there multiple options?
                3. OBSTACLES & CHALLENGES: What barriers or puzzles do you see?
                4. OBJECTIVES: Are there clear goals or targets visible?
                5. DIFFICULTY PROGRESSION: Does the layout suggest appropriate challenge scaling?
                6. PLAYER ENGAGEMENT: What elements would keep players interested?
                7. DESIGN STRENGTHS: What gameplay elements work well?
                8. IMPROVEMENT OPPORTUNITIES: What could enhance the player experience?
                
                Focus on player psychology, flow, and engagement principles.
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