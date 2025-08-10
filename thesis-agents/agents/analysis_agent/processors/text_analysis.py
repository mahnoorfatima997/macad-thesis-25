"""
Text analysis processing module for analyzing design briefs and textual content.
"""
from typing import List, Dict, Any, Optional
import re
from ..config import BUILDING_TYPE_PATTERNS, DETAIL_LEVEL_PATTERNS, COGNITIVE_PATTERNS
from ...common import TextProcessor, MetricsCalculator, AgentTelemetry


class TextAnalysisProcessor:
    """
    Processes text analysis for design briefs and content assessment.
    """
    
    def __init__(self):
        self.telemetry = AgentTelemetry("text_analysis")
        self.text_processor = TextProcessor()
        self.metrics_calculator = MetricsCalculator()
        
    def analyze_design_brief(self, brief: str) -> Dict[str, Any]:
        """
        Comprehensive analysis of design brief text.
        """
        self.telemetry.log_agent_start("analyze_design_brief")
        
        try:
            if not brief or len(brief.strip()) < 10:
                return self._get_empty_brief_analysis()
            
            # Core analysis components
            building_type = self._detect_building_type(brief)
            detail_level = self.assess_detail_level(brief)
            complexity_score = self._assess_complexity(brief)
            technical_depth = self._assess_technical_depth(brief)
            spatial_concepts = self._extract_spatial_concepts(brief)
            functional_requirements = self._extract_functional_requirements(brief)
            design_constraints = self._extract_design_constraints(brief)
            sustainability_aspects = self._extract_sustainability_aspects(brief)
            
            # Linguistic analysis
            word_count = len(brief.split())
            sentence_count = len(re.findall(r'[.!?]+', brief))
            avg_sentence_length = word_count / max(sentence_count, 1)
            
            # Semantic analysis
            key_themes = self._extract_key_themes(brief)
            design_intent = self._analyze_design_intent(brief)
            user_focus = self._analyze_user_focus(brief)
            
            return {
                "building_type": building_type,
                "detail_level": detail_level,
                "complexity_score": complexity_score,
                "technical_depth": technical_depth,
                "spatial_concepts": spatial_concepts,
                "functional_requirements": functional_requirements,
                "design_constraints": design_constraints,
                "sustainability_aspects": sustainability_aspects,
                "linguistic_metrics": {
                    "word_count": word_count,
                    "sentence_count": sentence_count,
                    "avg_sentence_length": avg_sentence_length
                },
                "semantic_analysis": {
                    "key_themes": key_themes,
                    "design_intent": design_intent,
                    "user_focus": user_focus
                },
                "brief_quality": self._assess_brief_quality(brief, word_count, detail_level),
                "analysis_timestamp": self.telemetry.get_timestamp()
            }
            
        except Exception as e:
            self.telemetry.log_error("analyze_design_brief", str(e))
            return self._get_fallback_brief_analysis(brief)
    
    def _detect_building_type(self, brief: str) -> str:
        """Detect building type from brief content."""
        try:
            brief_lower = brief.lower()
            type_scores = {}
            
            for building_type, patterns in BUILDING_TYPE_PATTERNS.items():
                score = 0
                for pattern in patterns:
                    if pattern.lower() in brief_lower:
                        score += 1
                type_scores[building_type] = score
            
            if type_scores and max(type_scores.values()) > 0:
                return max(type_scores, key=type_scores.get)
            else:
                return self._fallback_building_type_detection(brief)
                
        except Exception as e:
            self.telemetry.log_error("_detect_building_type", str(e))
            return "mixed-use"
    
    def _fallback_building_type_detection(self, brief: str) -> str:
        """Fallback building type detection using simple heuristics."""
        brief_lower = brief.lower()
        
        # Simple keyword-based detection
        if any(word in brief_lower for word in ["house", "home", "residential", "apartment"]):
            return "residential"
        elif any(word in brief_lower for word in ["office", "commercial", "retail", "business"]):
            return "commercial"
        elif any(word in brief_lower for word in ["school", "hospital", "library", "museum"]):
            return "institutional"
        elif any(word in brief_lower for word in ["factory", "warehouse", "industrial"]):
            return "industrial"
        else:
            return "mixed-use"
    
    def assess_detail_level(self, brief: str) -> str:
        """Assess the level of detail in the design brief."""
        try:
            brief_lower = brief.lower()
            level_scores = {}
            
            for level, patterns in DETAIL_LEVEL_PATTERNS.items():
                score = 0
                for pattern in patterns:
                    if pattern.lower() in brief_lower:
                        score += 1
                level_scores[level] = score
            
            # Also consider length as a factor
            word_count = len(brief.split())
            if word_count < 50:
                level_scores["low"] = level_scores.get("low", 0) + 2
            elif word_count > 200:
                level_scores["high"] = level_scores.get("high", 0) + 2
            else:
                level_scores["medium"] = level_scores.get("medium", 0) + 1
            
            if level_scores:
                return max(level_scores, key=level_scores.get)
            else:
                return "medium"
                
        except Exception as e:
            self.telemetry.log_error("assess_detail_level", str(e))
            return "medium"
    
    def _assess_complexity(self, brief: str) -> float:
        """Assess the complexity of the design brief."""
        try:
            complexity_indicators = [
                "integration", "coordination", "multiple", "complex", "sophisticated",
                "advanced", "innovative", "challenging", "interdisciplinary", "systems"
            ]
            
            brief_lower = brief.lower()
            complexity_count = sum(1 for indicator in complexity_indicators if indicator in brief_lower)
            
            # Normalize to 0-1 scale
            max_possible = len(complexity_indicators)
            complexity_score = min(complexity_count / max_possible, 1.0)
            
            return complexity_score
            
        except Exception as e:
            self.telemetry.log_error("_assess_complexity", str(e))
            return 0.5
    
    def _assess_technical_depth(self, brief: str) -> float:
        """Assess technical depth of the brief."""
        try:
            technical_terms = [
                "structure", "engineering", "systems", "mechanical", "electrical",
                "plumbing", "HVAC", "structural", "foundation", "materials",
                "specifications", "codes", "regulations", "standards", "performance"
            ]
            
            brief_lower = brief.lower()
            technical_count = sum(1 for term in technical_terms if term in brief_lower)
            
            # Normalize to 0-1 scale
            max_possible = len(technical_terms)
            technical_score = min(technical_count / max_possible, 1.0)
            
            return technical_score
            
        except Exception as e:
            self.telemetry.log_error("_assess_technical_depth", str(e))
            return 0.3
    
    def _extract_spatial_concepts(self, brief: str) -> List[str]:
        """Extract spatial concepts from the brief."""
        try:
            spatial_terms = [
                "open space", "circulation", "flow", "layout", "plan", "section",
                "spatial relationship", "adjacency", "hierarchy", "organization",
                "volume", "massing", "proportion", "scale", "orientation",
                "natural light", "views", "connection", "transition", "threshold"
            ]
            
            brief_lower = brief.lower()
            found_concepts = []
            
            for term in spatial_terms:
                if term in brief_lower:
                    found_concepts.append(term)
            
            return found_concepts
            
        except Exception as e:
            self.telemetry.log_error("_extract_spatial_concepts", str(e))
            return []
    
    def _extract_functional_requirements(self, brief: str) -> List[str]:
        """Extract functional requirements from the brief."""
        try:
            functional_terms = [
                "program", "function", "use", "activity", "purpose", "requirement",
                "needs", "accommodation", "capacity", "occupancy", "accessibility",
                "flexibility", "adaptability", "efficiency", "workflow", "operations"
            ]
            
            brief_lower = brief.lower()
            found_requirements = []
            
            for term in functional_terms:
                if term in brief_lower:
                    found_requirements.append(term)
            
            # Also extract room types and spaces mentioned
            room_patterns = [
                "bedroom", "bathroom", "kitchen", "living room", "office", "meeting room",
                "classroom", "laboratory", "workshop", "storage", "lobby", "entrance"
            ]
            
            for pattern in room_patterns:
                if pattern in brief_lower:
                    found_requirements.append(pattern)
            
            return found_requirements
            
        except Exception as e:
            self.telemetry.log_error("_extract_functional_requirements", str(e))
            return []
    
    def _extract_design_constraints(self, brief: str) -> List[str]:
        """Extract design constraints from the brief."""
        try:
            constraint_terms = [
                "budget", "cost", "timeline", "schedule", "site", "zoning",
                "regulations", "codes", "restrictions", "limitations", "constraints",
                "climate", "environment", "context", "existing", "heritage"
            ]
            
            brief_lower = brief.lower()
            found_constraints = []
            
            for term in constraint_terms:
                if term in brief_lower:
                    found_constraints.append(term)
            
            return found_constraints
            
        except Exception as e:
            self.telemetry.log_error("_extract_design_constraints", str(e))
            return []
    
    def _extract_sustainability_aspects(self, brief: str) -> List[str]:
        """Extract sustainability-related aspects from the brief."""
        try:
            sustainability_terms = [
                "sustainable", "sustainability", "green", "eco", "environmental",
                "energy efficient", "renewable", "solar", "passive", "natural ventilation",
                "daylight", "water conservation", "recycled materials", "carbon neutral",
                "LEED", "BREEAM", "passive house", "net zero", "resilient"
            ]
            
            brief_lower = brief.lower()
            found_aspects = []
            
            for term in sustainability_terms:
                if term in brief_lower:
                    found_aspects.append(term)
            
            return found_aspects
            
        except Exception as e:
            self.telemetry.log_error("_extract_sustainability_aspects", str(e))
            return []
    
    def _extract_key_themes(self, brief: str) -> List[str]:
        """Extract key themes from the brief."""
        try:
            # Simple theme extraction based on frequency and importance
            words = re.findall(r'\b\w+\b', brief.lower())
            
            # Filter out common words
            stop_words = {"the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
            filtered_words = [word for word in words if len(word) > 3 and word not in stop_words]
            
            # Count frequency
            word_freq = {}
            for word in filtered_words:
                word_freq[word] = word_freq.get(word, 0) + 1
            
            # Get most frequent words as themes
            themes = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
            return [theme[0] for theme in themes]
            
        except Exception as e:
            self.telemetry.log_error("_extract_key_themes", str(e))
            return []
    
    def _analyze_design_intent(self, brief: str) -> str:
        """Analyze the design intent expressed in the brief."""
        try:
            intent_indicators = {
                "innovative": ["innovative", "cutting-edge", "pioneering", "revolutionary", "breakthrough"],
                "traditional": ["traditional", "classic", "timeless", "heritage", "vernacular"],
                "functional": ["functional", "practical", "efficient", "utilitarian", "performance"],
                "aesthetic": ["beautiful", "elegant", "striking", "artistic", "sculptural"],
                "sustainable": ["sustainable", "green", "eco-friendly", "environmentally", "renewable"]
            }
            
            brief_lower = brief.lower()
            intent_scores = {}
            
            for intent, indicators in intent_indicators.items():
                score = sum(1 for indicator in indicators if indicator in brief_lower)
                intent_scores[intent] = score
            
            if intent_scores and max(intent_scores.values()) > 0:
                return max(intent_scores, key=intent_scores.get)
            else:
                return "balanced"
                
        except Exception as e:
            self.telemetry.log_error("_analyze_design_intent", str(e))
            return "balanced"
    
    def _analyze_user_focus(self, brief: str) -> str:
        """Analyze the user focus of the brief."""
        try:
            user_indicators = {
                "community": ["community", "public", "social", "collective", "shared"],
                "individual": ["private", "personal", "individual", "intimate", "exclusive"],
                "family": ["family", "household", "domestic", "residential", "home"],
                "professional": ["office", "workplace", "business", "commercial", "corporate"],
                "educational": ["learning", "education", "teaching", "academic", "student"]
            }
            
            brief_lower = brief.lower()
            focus_scores = {}
            
            for focus, indicators in user_indicators.items():
                score = sum(1 for indicator in indicators if indicator in brief_lower)
                focus_scores[focus] = score
            
            if focus_scores and max(focus_scores.values()) > 0:
                return max(focus_scores, key=focus_scores.get)
            else:
                return "general"
                
        except Exception as e:
            self.telemetry.log_error("_analyze_user_focus", str(e))
            return "general"
    
    def _assess_brief_quality(self, brief: str, word_count: int, detail_level: str) -> str:
        """Assess overall quality of the design brief."""
        try:
            quality_score = 0
            
            # Length factor
            if 50 <= word_count <= 300:
                quality_score += 2
            elif word_count > 10:
                quality_score += 1
            
            # Detail level factor
            detail_scores = {"high": 3, "medium": 2, "low": 1}
            quality_score += detail_scores.get(detail_level, 1)
            
            # Content richness (presence of different aspects)
            content_aspects = [
                any(term in brief.lower() for term in ["function", "program", "use"]),
                any(term in brief.lower() for term in ["site", "location", "context"]),
                any(term in brief.lower() for term in ["user", "client", "occupant"]),
                any(term in brief.lower() for term in ["aesthetic", "style", "character"]),
                any(term in brief.lower() for term in ["budget", "cost", "timeline"])
            ]
            
            quality_score += sum(content_aspects)
            
            # Quality categories
            if quality_score >= 8:
                return "excellent"
            elif quality_score >= 6:
                return "good"
            elif quality_score >= 4:
                return "adequate"
            else:
                return "needs_improvement"
                
        except Exception as e:
            self.telemetry.log_error("_assess_brief_quality", str(e))
            return "adequate"
    
    def _get_empty_brief_analysis(self) -> Dict[str, Any]:
        """Return analysis for empty or very short briefs."""
        return {
            "building_type": "unknown",
            "detail_level": "low",
            "complexity_score": 0.0,
            "technical_depth": 0.0,
            "spatial_concepts": [],
            "functional_requirements": [],
            "design_constraints": [],
            "sustainability_aspects": [],
            "linguistic_metrics": {
                "word_count": 0,
                "sentence_count": 0,
                "avg_sentence_length": 0
            },
            "semantic_analysis": {
                "key_themes": [],
                "design_intent": "unclear",
                "user_focus": "unknown"
            },
            "brief_quality": "needs_improvement",
            "analysis_timestamp": self.telemetry.get_timestamp()
        }
    
    def _get_fallback_brief_analysis(self, brief: str) -> Dict[str, Any]:
        """Return fallback analysis when main analysis fails."""
        return {
            "building_type": "mixed-use",
            "detail_level": "medium",
            "complexity_score": 0.5,
            "technical_depth": 0.3,
            "spatial_concepts": [],
            "functional_requirements": [],
            "design_constraints": [],
            "sustainability_aspects": [],
            "linguistic_metrics": {
                "word_count": len(brief.split()) if brief else 0,
                "sentence_count": 1,
                "avg_sentence_length": len(brief.split()) if brief else 0
            },
            "semantic_analysis": {
                "key_themes": [],
                "design_intent": "balanced",
                "user_focus": "general"
            },
            "brief_quality": "adequate",
            "analysis_timestamp": self.telemetry.get_timestamp()
        } 