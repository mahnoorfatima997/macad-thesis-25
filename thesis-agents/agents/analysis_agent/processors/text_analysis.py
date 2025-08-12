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
        """Enhanced building type detection with confidence scoring and intelligent fallback."""
        try:
            brief_lower = brief.lower()
            type_scores = {}
            
            # Enhanced building type detection patterns (matching other components)
            detection_patterns = [
                # High Priority - Specific building types
                ("learning_center", ["learning center", "education center", "learning hub", "training center", "skill center", "study center", "workshop center", "kindergarten"], 10),
                ("community_center", ["community center", "community facility", "civic center", "public center", "social hub", "gathering place", "neighborhood center", "town hall", "community center for sports", "community sports center"], 10),
                ("sports_center", ["sports center", "fitness center", "gym", "athletic center", "sports facility", "fitness facility", "athletic facility", "sports complex", "recreation center", "activity center"], 10),
                ("cultural_institution", ["museum", "gallery", "theater", "cultural center", "arts center", "performance center", "exhibition center", "cultural hub", "heritage center"], 10),
                ("library", ["library", "librarian", "reading room", "study space", "research center", "information center", "book center"], 10),
                ("research_facility", ["research facility", "laboratory", "lab", "research center", "innovation center", "development center", "testing facility"], 10),
                
                # High Priority - Healthcare
                ("hospital", ["hospital", "medical center", "health center", "clinic", "medical facility", "healthcare facility", "treatment center"], 9),
                ("specialized_clinic", ["specialized clinic", "specialty clinic", "medical clinic", "health clinic", "outpatient clinic", "diagnostic center"], 9),
                ("wellness_center", ["wellness center", "health center", "medical spa", "holistic center", "alternative medicine", "wellness facility"], 9),
                ("rehabilitation_center", ["rehabilitation center", "rehab center", "recovery center", "therapy center", "treatment facility"], 9),
                
                # High Priority - Educational
                ("educational", ["school", "university", "college", "classroom", "educational", "learning", "academy", "institute"], 9),
                
                # Medium Priority - Residential
                ("residential", ["house", "home", "apartment", "residential", "housing", "dwelling", "residence", "domestic"], 8),
                ("multi_family", ["multi-family", "apartment building", "condominium", "townhouse", "duplex", "triplex", "residential complex"], 8),
                ("senior_housing", ["senior housing", "elderly housing", "retirement community", "assisted living", "nursing home", "care facility"], 8),
                ("student_housing", ["student housing", "dormitory", "student residence", "college housing", "university housing"], 8),
                
                # Medium Priority - Commercial
                ("office", ["office", "workplace", "corporate", "business", "commercial", "workspace", "professional", "executive"], 7),
                ("retail", ["store", "shop", "retail", "commercial", "market", "shopping", "merchant", "boutique"], 7),
                ("restaurant", ["restaurant", "cafe", "dining", "eatery", "bistro", "food service", "culinary", "dining establishment"], 7),
                ("hotel", ["hotel", "lodging", "accommodation", "inn", "resort", "guesthouse", "hostel", "bed and breakfast"], 7),
                
                # Medium Priority - Community & Recreation
                ("recreation_center", ["recreation center", "leisure center", "entertainment center"], 7),
                ("senior_center", ["senior center", "elderly center", "aging center", "retirement center", "adult center", "mature center"], 7),
                ("youth_center", ["youth center", "teen center", "adolescent center", "young center", "teenager center"], 7),
                
                # Medium Priority - Industrial
                ("industrial", ["factory", "warehouse", "industrial", "manufacturing", "production", "industrial facility", "manufacturing plant"], 6),
                ("logistics_center", ["logistics center", "distribution center", "fulfillment center", "storage facility", "warehouse facility"], 6),
                ("research_industrial", ["research and development", "R&D facility", "innovation center", "technology center", "development facility"], 6),
                
                # Medium Priority - Transportation
                ("transportation_hub", ["transportation hub", "transit center", "transport hub", "mobility center", "travel center"], 6),
                ("parking_facility", ["parking facility", "parking garage", "parking structure", "parking center", "car park"], 6),
                ("maintenance_facility", ["maintenance facility", "service center", "repair facility", "maintenance center"], 6),
                
                # Lower Priority - Religious & Spiritual
                ("religious", ["church", "temple", "mosque", "synagogue", "religious", "worship", "spiritual", "sacred", "faith center"], 5),
                ("meditation_center", ["meditation center", "spiritual center", "zen center", "mindfulness center", "contemplation center"], 5),
                
                # Lower Priority - Agricultural & Environmental
                ("agricultural", ["farm", "agricultural", "greenhouse", "nursery", "agricultural facility", "farming center"], 4),
                ("environmental_center", ["environmental center", "nature center", "conservation center", "ecology center", "sustainability center"], 4),
                
                # Lower Priority - Specialized
                ("conference_center", ["conference center", "convention center", "meeting center", "event center", "summit center"], 4),
                ("innovation_hub", ["innovation hub", "startup center", "entrepreneurial center", "business incubator", "tech hub"], 4),
                ("creative_workspace", ["creative workspace", "artist studio", "design studio", "creative center", "artistic space"], 4),
                
                # Lower Priority - Government & Public
                ("government", ["government building", "civic building", "public building", "administrative center", "public service"], 3),
                ("emergency_services", ["fire station", "police station", "emergency center", "public safety", "emergency facility"], 3),
                ("utility_facility", ["utility facility", "power plant", "water treatment", "energy center", "infrastructure facility"], 3),
                
                # Lowest Priority - Mixed Use
                ("mixed_use", ["mixed use", "multi-use", "combined use", "integrated", "hybrid", "versatile", "flexible"], 2)
            ]
            
            # Score each building type based on keyword matches
            for building_type, keywords, base_priority in detection_patterns:
                score = 0
                for keyword in keywords:
                    if keyword in brief_lower:
                        score += base_priority
                        # Bonus for exact matches
                        if keyword == brief_lower.strip():
                            score += 5
                        # Bonus for longer, more specific keywords
                        if len(keyword.split()) > 1:
                            score += 2
                        # Bonus for multiple keyword matches
                        if brief_lower.count(keyword) > 1:
                            score += 1
                
                if score > 0:
                    type_scores[building_type] = score
            
            # Return the highest scoring building type if confidence is high enough
            if type_scores and max(type_scores.values()) >= 5:
                best_type = max(type_scores, key=type_scores.get)
                confidence_score = type_scores[best_type]
                
                # Log the detection for debugging
                print(f"🏗️ Building type detected: {best_type} (confidence: {confidence_score})")
                
                return best_type
            else:
                # Fallback to enhanced detection if no high-confidence match
                return self._fallback_building_type_detection(brief)
                
        except Exception as e:
            self.telemetry.log_error("_detect_building_type", str(e))
            return self._fallback_building_type_detection(brief)
    
    def _fallback_building_type_detection(self, brief: str) -> str:
        """Enhanced fallback building type detection using intelligent heuristics and priority scoring."""
        brief_lower = brief.lower()
        
        # Define detection patterns with priority scores
        detection_patterns = [
            # High Priority - Specific building types
            ("learning_center", ["learning center", "education center", "learning hub", "training center", "skill center", "study center", "workshop center"], 10),
            ("community_center", ["community center", "community facility", "civic center", "public center", "social hub", "gathering place", "neighborhood center", "town hall"], 10),
            ("cultural_institution", ["museum", "gallery", "theater", "cultural center", "arts center", "performance center", "exhibition center", "cultural hub", "heritage center"], 10),
            ("library", ["library", "librarian", "reading room", "study space", "research center", "information center", "book center"], 10),
            ("research_facility", ["research facility", "laboratory", "lab", "research center", "innovation center", "development center", "testing facility"], 10),
            
            # High Priority - Healthcare
            ("hospital", ["hospital", "medical center", "health center", "clinic", "medical facility", "healthcare facility", "treatment center"], 9),
            ("specialized_clinic", ["specialized clinic", "specialty clinic", "medical clinic", "health clinic", "outpatient clinic", "diagnostic center"], 9),
            ("wellness_center", ["wellness center", "health center", "medical spa", "holistic center", "alternative medicine", "wellness facility"], 9),
            ("rehabilitation_center", ["rehabilitation center", "rehab center", "recovery center", "therapy center", "treatment facility"], 9),
            
            # High Priority - Educational
            ("educational", ["school", "university", "college", "classroom", "educational", "learning", "academy", "institute"], 9),
            
            # Medium Priority - Residential
            ("residential", ["house", "home", "apartment", "residential", "housing", "dwelling", "residence", "domestic"], 8),
            ("multi_family", ["multi-family", "apartment building", "condominium", "townhouse", "duplex", "triplex", "residential complex"], 8),
            ("senior_housing", ["senior housing", "elderly housing", "retirement community", "assisted living", "nursing home", "care facility"], 8),
            ("student_housing", ["student housing", "dormitory", "student residence", "college housing", "university housing"], 8),
            
            # Medium Priority - Commercial
            ("office", ["office", "workplace", "corporate", "business", "commercial", "workspace", "professional", "executive"], 7),
            ("retail", ["store", "shop", "retail", "commercial", "market", "shopping", "merchant", "boutique"], 7),
            ("restaurant", ["restaurant", "cafe", "dining", "eatery", "bistro", "food service", "culinary", "dining establishment"], 7),
            ("hotel", ["hotel", "lodging", "accommodation", "inn", "resort", "guesthouse", "hostel", "bed and breakfast"], 7),
            
            # Medium Priority - Community & Recreation
            ("recreation_center", ["recreation center", "sports center", "fitness center", "wellness center", "activity center", "leisure center", "entertainment center"], 7),
            ("senior_center", ["senior center", "elderly center", "aging center", "retirement center", "adult center", "mature center"], 7),
            ("youth_center", ["youth center", "teen center", "adolescent center", "young center", "teenager center"], 7),
            
            # Medium Priority - Industrial
            ("industrial", ["factory", "warehouse", "industrial", "manufacturing", "production", "industrial facility", "manufacturing plant"], 6),
            ("logistics_center", ["logistics center", "distribution center", "fulfillment center", "storage facility", "warehouse facility"], 6),
            ("research_industrial", ["research and development", "R&D facility", "innovation center", "technology center", "development facility"], 6),
            
            # Medium Priority - Transportation
            ("transportation_hub", ["transportation hub", "transit center", "transport hub", "mobility center", "travel center"], 6),
            ("parking_facility", ["parking facility", "parking garage", "parking structure", "parking center", "car park"], 6),
            ("maintenance_facility", ["maintenance facility", "service center", "repair facility", "maintenance center"], 6),
            
            # Lower Priority - Religious & Spiritual
            ("religious", ["church", "temple", "mosque", "synagogue", "religious", "worship", "spiritual", "sacred", "faith center"], 5),
            ("meditation_center", ["meditation center", "spiritual center", "zen center", "mindfulness center", "contemplation center"], 5),
            
            # Lower Priority - Agricultural & Environmental
            ("agricultural", ["farm", "agricultural", "greenhouse", "nursery", "agricultural facility", "farming center"], 4),
            ("environmental_center", ["environmental center", "nature center", "conservation center", "ecology center", "sustainability center"], 4),
            
            # Lower Priority - Specialized
            ("conference_center", ["conference center", "convention center", "meeting center", "event center", "summit center"], 4),
            ("innovation_hub", ["innovation hub", "startup center", "entrepreneurial center", "business incubator", "tech hub"], 4),
            ("creative_workspace", ["creative workspace", "artist studio", "design studio", "creative center", "artistic space"], 4),
            
            # Lower Priority - Government & Public
            ("government", ["government building", "civic building", "public building", "administrative center", "public service"], 3),
            ("emergency_services", ["fire station", "police station", "emergency center", "public safety", "emergency facility"], 3),
            ("utility_facility", ["utility facility", "power plant", "water treatment", "energy center", "infrastructure facility"], 3),
            
            # Lowest Priority - Mixed Use
            ("mixed_use", ["mixed use", "multi-use", "combined use", "integrated", "hybrid", "versatile", "flexible"], 2)
        ]
        
        # Score each building type based on keyword matches
        building_scores = {}
        for building_type, keywords, base_priority in detection_patterns:
            score = 0
            for keyword in keywords:
                if keyword in brief_lower:
                    score += base_priority
                    # Bonus for exact matches
                    if keyword == brief_lower.strip():
                        score += 5
                    # Bonus for longer, more specific keywords
                    if len(keyword.split()) > 1:
                        score += 2
            
            if score > 0:
                building_scores[building_type] = score
        
        # Return the highest scoring building type, or mixed_use as fallback
        if building_scores:
            best_match = max(building_scores, key=building_scores.get)
            # Only return specific types if score is high enough
            if building_scores[best_match] >= 5:
                return best_match
        
        return "mixed_use"
    
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

    def get_building_type_context(self, building_type: str) -> Dict[str, Any]:
        """Get comprehensive context and characteristics for a building type."""
        
        building_contexts = {
            "learning_center": {
                "description": "A facility focused on education, skill development, and knowledge sharing",
                "key_considerations": ["flexible learning spaces", "technology integration", "accessibility", "acoustic design", "natural lighting"],
                "typical_users": ["students", "professionals", "community members", "instructors"],
                "spatial_priorities": ["classrooms", "study areas", "collaborative spaces", "technology labs", "quiet zones"],
                "sustainability_focus": ["energy efficiency", "indoor air quality", "daylighting", "flexible systems"]
            },
            "community_center": {
                "description": "A multi-purpose facility serving community needs and fostering social connections",
                "key_considerations": ["versatile spaces", "community engagement", "accessibility", "multi-generational design", "flexible programming"],
                "typical_users": ["all ages", "community groups", "local organizations", "families"],
                "spatial_priorities": ["multi-purpose rooms", "gathering spaces", "activity areas", "meeting rooms", "outdoor spaces"],
                "sustainability_focus": ["community connection", "local materials", "flexible design", "social sustainability"]
            },
            "cultural_institution": {
                "description": "A facility dedicated to arts, culture, heritage, and creative expression",
                "key_considerations": ["exhibition spaces", "performance venues", "cultural sensitivity", "visitor experience", "preservation"],
                "typical_users": ["visitors", "artists", "performers", "researchers", "students"],
                "spatial_priorities": ["galleries", "theaters", "workshops", "storage", "public spaces"],
                "sustainability_focus": ["cultural preservation", "adaptive reuse", "visitor comfort", "long-term value"]
            },
            "library": {
                "description": "A facility for information access, study, and community learning",
                "key_considerations": ["quiet study areas", "technology access", "flexible seating", "acoustic design", "natural lighting"],
                "typical_users": ["students", "researchers", "community members", "professionals"],
                "spatial_priorities": ["reading rooms", "study carrels", "group study areas", "technology centers", "quiet zones"],
                "sustainability_focus": ["daylighting", "energy efficiency", "indoor air quality", "flexible systems"]
            },
            "research_facility": {
                "description": "A facility designed for scientific research, development, and innovation",
                "key_considerations": ["laboratory safety", "flexible research spaces", "technology infrastructure", "collaboration areas", "security"],
                "typical_users": ["researchers", "scientists", "students", "technicians"],
                "spatial_priorities": ["laboratories", "research offices", "collaboration spaces", "equipment rooms", "support spaces"],
                "sustainability_focus": ["energy efficiency", "safety systems", "flexible infrastructure", "technology integration"]
            },
            "hospital": {
                "description": "A comprehensive healthcare facility providing medical treatment and care",
                "key_considerations": ["patient safety", "infection control", "accessibility", "efficiency", "patient comfort"],
                "typical_users": ["patients", "medical staff", "visitors", "administrative staff"],
                "spatial_priorities": ["patient rooms", "operating rooms", "emergency departments", "diagnostic areas", "support services"],
                "sustainability_focus": ["infection control", "energy efficiency", "patient safety", "operational efficiency"]
            },
            "residential": {
                "description": "A facility designed for living and domestic activities",
                "key_considerations": ["privacy", "comfort", "functionality", "personalization", "community connection"],
                "typical_users": ["residents", "families", "individuals", "guests"],
                "spatial_priorities": ["living areas", "bedrooms", "kitchens", "bathrooms", "outdoor spaces"],
                "sustainability_focus": ["energy efficiency", "comfort", "durability", "personal well-being"]
            },
            "office": {
                "description": "A facility designed for professional work and business activities",
                "key_considerations": ["productivity", "collaboration", "technology integration", "comfort", "flexibility"],
                "typical_users": ["employees", "clients", "visitors", "service providers"],
                "spatial_priorities": ["workstations", "meeting rooms", "collaboration areas", "support spaces", "reception areas"],
                "sustainability_focus": ["energy efficiency", "indoor air quality", "daylighting", "flexible systems"]
            },
            "mixed_use": {
                "description": "A facility combining multiple functions and building types",
                "key_considerations": ["functional integration", "circulation", "noise separation", "flexibility", "community interaction"],
                "typical_users": ["various user groups", "residents", "workers", "visitors"],
                "spatial_priorities": ["functional zones", "circulation systems", "shared spaces", "service areas", "outdoor connections"],
                "sustainability_focus": ["functional efficiency", "community interaction", "resource sharing", "flexible design"]
            }
        }
        
        return building_contexts.get(building_type, {
            "description": "A specialized facility with unique requirements",
            "key_considerations": ["functionality", "user needs", "context", "sustainability"],
            "typical_users": ["various users", "specialized groups"],
            "spatial_priorities": ["functional spaces", "support areas", "circulation"],
            "sustainability_focus": ["efficiency", "user comfort", "long-term value"]
        })
    
    def analyze_building_type_requirements(self, building_type: str, brief: str) -> Dict[str, Any]:
        """Analyze specific requirements for a building type based on the brief."""
        
        context = self.get_building_type_context(building_type)
        brief_lower = brief.lower()
        
        # Analyze specific requirements mentioned in the brief
        requirements = {
            "accessibility": any(word in brief_lower for word in ["accessible", "disability", "wheelchair", "universal design", "inclusive"]),
            "sustainability": any(word in brief_lower for word in ["sustainable", "green", "eco-friendly", "energy efficient", "LEED", "passive"]),
            "technology": any(word in brief_lower for word in ["smart", "technology", "digital", "automated", "connected"]),
            "flexibility": any(word in brief_lower for word in ["flexible", "adaptable", "versatile", "multi-purpose", "changeable"]),
            "community": any(word in brief_lower for word in ["community", "social", "interactive", "collaborative", "gathering"]),
            "security": any(word in brief_lower for word in ["secure", "safety", "protected", "controlled access", "surveillance"]),
            "acoustics": any(word in brief_lower for word in ["acoustic", "sound", "noise", "quiet", "audio"]),
            "lighting": any(word in brief_lower for word in ["lighting", "daylight", "natural light", "illumination", "bright"])
        }
        
        # Calculate priority score for requirements
        requirement_priorities = {}
        for req, present in requirements.items():
            if present:
                # Base priority based on building type
                base_priority = 5
                if req in context["key_considerations"]:
                    base_priority += 3
                if req in context["sustainability_focus"]:
                    base_priority += 2
                requirement_priorities[req] = base_priority
        
        return {
            "building_type": building_type,
            "context": context,
            "requirements": requirements,
            "requirement_priorities": requirement_priorities,
            "brief_analysis": {
                "word_count": len(brief.split()),
                "complexity": "high" if len(brief.split()) > 100 else "medium" if len(brief.split()) > 50 else "low",
                "specificity": "high" if any(req for req in requirements.values()) else "low"
            }
        } 