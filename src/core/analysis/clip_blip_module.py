#!/usr/bin/env python3
"""
CLIP/BLIP Analysis Module
Clean, focused CLIP and BLIP models for visual analysis of architectural images
"""

import os
import base64
from typing import Dict, Any, List, Optional
from PIL import Image
import numpy as np
import tempfile

# CLIP/BLIP imports
try:
    import torch
    from transformers import CLIPProcessor, CLIPModel, BlipProcessor, BlipForConditionalGeneration
    CLIP_BLIP_AVAILABLE = True
except ImportError:
    CLIP_BLIP_AVAILABLE = False
    print("⚠️ CLIP/BLIP not available. Install transformers package.")

class CLIPBLIPAnalyzer:
    """Clean CLIP/BLIP analyzer for architectural visual analysis"""
    
    def __init__(self):
        """Initialize CLIP/BLIP analyzer"""
        self.clip_model = None
        self.clip_processor = None
        self.blip_model = None
        self.blip_processor = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Load models
        if CLIP_BLIP_AVAILABLE:
            self._load_models()
        else:
            print("❌ CLIP/BLIP not available - install transformers package")
    
    def _load_models(self):
        """Load CLIP and BLIP models"""
        try:
            print("Loading CLIP model...")
            self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
            self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
            self.clip_model.to(self.device)
            print("✓ CLIP model loaded successfully")
            
            print("Loading BLIP model...")
            self.blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
            self.blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
            self.blip_model.to(self.device)
            print("✓ BLIP model loaded successfully")
            
        except Exception as e:
            print(f"❌ Error loading CLIP/BLIP models: {e}")
            self.clip_model = None
            self.blip_model = None
    
    def analyze_image(self, image_path: str) -> Dict[str, Any]:
        """
        Analyze image using CLIP and BLIP
        
        Args:
            image_path (str): Path to input image
            
        Returns:
            dict: Analysis results from both models
        """
        if self.clip_model is None or self.blip_model is None:
            return {"error": "CLIP/BLIP models not loaded", "analysis": {}}
        
        try:
            # Load and preprocess image
            pil_image = Image.open(image_path).convert('RGB')
            
            # Get BLIP caption
            blip_caption = self._generate_blip_caption(pil_image)
            
            # Get CLIP analysis
            clip_analysis = self._analyze_clip_concepts(pil_image)
            
            # Combine results
            analysis = {
                "blip_caption": blip_caption,
                "clip_concepts": clip_analysis,
                "combined_insights": self._combine_insights(blip_caption, clip_analysis)
            }
            
            return {
                "analysis": analysis,
                "models_used": ["CLIP", "BLIP"],
                "image_path": image_path
            }
            
        except Exception as e:
            return {"error": f"Analysis failed: {e}", "analysis": {}}
    
    def _generate_blip_caption(self, pil_image: Image.Image) -> str:
        """Generate caption using BLIP"""
        try:
            inputs = self.blip_processor(pil_image, return_tensors="pt").to(self.device)
            out = self.blip_model.generate(**inputs, max_length=50)
            caption = self.blip_processor.decode(out[0], skip_special_tokens=True)
            return caption
        except Exception as e:
            print(f"BLIP caption generation failed: {e}")
            return "Unable to generate caption"
    
    def _analyze_clip_concepts(self, pil_image: Image.Image) -> Dict[str, float]:
        """Analyze image concepts using CLIP"""
        try:
            # Architectural concepts to test
            concepts = [
                "modern building", "traditional architecture", "residential building", 
                "commercial building", "open floor plan", "closed floor plan",
                "large windows", "small windows", "natural lighting", "artificial lighting",
                "spacious rooms", "compact rooms", "high ceilings", "low ceilings",
                "wooden materials", "concrete materials", "glass facade", "brick facade",
                "sustainable design", "luxury design", "minimalist design", "ornate design",
                "good circulation", "poor circulation", "accessible design", "inaccessible design",
                "energy efficient", "energy inefficient", "well organized", "poorly organized"
            ]
            
            # Process image and text
            inputs = self.clip_processor(
                text=concepts,
                images=pil_image,
                return_tensors="pt",
                padding=True
            ).to(self.device)
            
            # Get predictions
            outputs = self.clip_model(**inputs)
            logits_per_image = outputs.logits_per_image
            probs = logits_per_image.softmax(dim=-1)
            
            # Convert to dictionary
            concept_scores = {}
            for i, concept in enumerate(concepts):
                concept_scores[concept] = float(probs[0][i])
            
            return concept_scores
            
        except Exception as e:
            print(f"CLIP concept analysis failed: {e}")
            return {}
    
    def _combine_insights(self, blip_caption: str, clip_concepts: Dict[str, float]) -> Dict[str, Any]:
        """Combine insights from BLIP and CLIP"""
        insights = {
            "overall_description": blip_caption,
            "key_characteristics": [],
            "design_quality": {},
            "architectural_style": {},
            "functional_aspects": {},
            "environmental_aspects": {}
        }
        
        # Extract key characteristics from CLIP concepts
        if clip_concepts:
            # Sort concepts by score
            sorted_concepts = sorted(clip_concepts.items(), key=lambda x: x[1], reverse=True)
            
            # Get top characteristics
            insights["key_characteristics"] = [concept for concept, score in sorted_concepts[:10] if score > 0.1]
            
            # Categorize concepts
            for concept, score in clip_concepts.items():
                if score > 0.1:  # Only consider significant scores
                    if "modern" in concept or "traditional" in concept or "minimalist" in concept:
                        insights["architectural_style"][concept] = score
                    elif "lighting" in concept or "circulation" in concept or "organized" in concept:
                        insights["functional_aspects"][concept] = score
                    elif "sustainable" in concept or "energy" in concept:
                        insights["environmental_aspects"][concept] = score
                    elif "good" in concept or "poor" in concept or "quality" in concept:
                        insights["design_quality"][concept] = score
        
        return insights
    
    def get_analysis_summary(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate summary of analysis results
        
        Args:
            analysis (dict): Analysis results
            
        Returns:
            dict: Summary statistics
        """
        if not analysis:
            return {"total_concepts": 0, "key_insights": [], "overall_score": 0.0}
        
        insights = analysis.get("combined_insights", {})
        
        # Calculate overall score
        clip_concepts = analysis.get("clip_concepts", {})
        if clip_concepts:
            positive_concepts = [score for concept, score in clip_concepts.items() 
                               if "good" in concept or "well" in concept or "efficient" in concept]
            negative_concepts = [score for concept, score in clip_concepts.items() 
                               if "poor" in concept or "bad" in concept or "inefficient" in concept]
            
            positive_score = sum(positive_concepts) / len(positive_concepts) if positive_concepts else 0
            negative_score = sum(negative_concepts) / len(negative_concepts) if negative_concepts else 0
            overall_score = positive_score - negative_score
        else:
            overall_score = 0.0
        
        return {
            "total_concepts": len(clip_concepts),
            "key_insights": insights.get("key_characteristics", []),
            "overall_score": overall_score,
            "architectural_style": list(insights.get("architectural_style", {}).keys()),
            "functional_aspects": list(insights.get("functional_aspects", {}).keys())
        } 