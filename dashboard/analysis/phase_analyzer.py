"""
Phase progression and conversation analysis for the dashboard.
"""

from typing import Dict, List, Any, Tuple


class PhaseAnalyzer:
    """Analyzer for design phase progression and conversation patterns."""
    
    # Phase detection keywords
    PHASE_KEYWORDS = {
        "ideation": [
            "concept", "idea", "approach", "strategy", "vision", "goal", "objective", 
            "purpose", "intention", "brainstorm", "explore", "consider", "think about", 
            "what if", "imagine", "envision", "precedent", "example", "reference", 
            "inspiration", "influence", "site", "context", "requirements", "program",
            "need", "want", "should", "could", "might", "maybe", "perhaps"
        ],
        "visualization": [
            "form", "shape", "massing", "volume", "proportion", "scale", "circulation", 
            "flow", "layout", "plan", "section", "elevation", "sketch", "drawing", 
            "model", "3d", "render", "visualize", "spatial", "arrangement", 
            "composition", "geometry", "structure", "lighting", "spatial organization",
            "room", "space", "area", "zone", "floor", "level", "height", "width",
            "dimension", "size", "placement", "position", "orientation"
        ],
        "materialization": [
            "construction", "structure", "system", "detail", "material", "technical", 
            "engineering", "performance", "cost", "budget", "timeline", "schedule", 
            "specification", "implementation", "fabrication", "assembly", "installation", 
            "maintenance", "durability", "sustainability", "efficiency", "code", "standard",
            "wall", "floor", "ceiling", "door", "window", "roof", "foundation"
        ]
    }
    
    def calculate_conversation_progress(self, chat_interactions: List[Dict]) -> Tuple[str, float]:
        """Deprecated heuristic: retained for compatibility but returns zero progress.

        Phase and percent should come from the PhaseProgressionSystem engine.
        """
        if not chat_interactions:
            return "ideation", 0.0
        # Keep lightweight phase guess for legacy callers, but do not compute percent
        all_text = " ".join([
            f"{i.get('data', {}).get('input', '')} {i.get('data', {}).get('response', '')}"
            for i in chat_interactions
        ]).lower()
        phase_scores = {"ideation": 0, "visualization": 0, "materialization": 0}
        for phase, keywords in self.PHASE_KEYWORDS.items():
            for keyword in keywords:
                if keyword in all_text:
                    phase_scores[phase] += 1
        current_phase = max(phase_scores, key=phase_scores.get)
        return current_phase, 0.0
    
    def analyze_phase_progression(self, interactions: List[Dict]) -> Dict[str, Any]:
        """Analyze conversation to extract challenges and learning points.

        Note: Phase percent should come from the engine; this provides qualitative insights only.
        """
        if not interactions:
            return {
                "current_phase": "ideation",
                "phase_progress": 0,
                "session_duration": "Active",
                "challenges": [
                    "Understanding project requirements and constraints",
                    "Balancing functionality with aesthetic considerations",
                    "Integrating sustainable design principles effectively"
                ],
                "learning_points": [
                    "Developing systematic approach to design problems",
                    "Enhancing spatial reasoning and visualization skills",
                    "Improving design communication and presentation"
                ]
            }

        content_text = " ".join([
            f"{str(i.get('data', {}).get('input', ''))} {str(i.get('data', {}).get('response', ''))}"
            for i in interactions
        ])
        content_lower = content_text.lower()

        # Lightweight phase guess (not used for percent)
        phase_scores = {p: 0 for p in self.PHASE_KEYWORDS.keys()}
        for phase, keywords in self.PHASE_KEYWORDS.items():
            phase_scores[phase] = sum(1 for k in keywords if k in content_lower)
        current_phase = max(phase_scores, key=phase_scores.get) if phase_scores else "ideation"

        # Extract lists
        challenges = self._identify_challenges(content_lower)
        learning_points = self._identify_learning_points(content_lower, interactions)

        return {
            "current_phase": current_phase,
            "phase_progress": 0,
            "session_duration": "Active",
            "challenges": challenges,
            "learning_points": learning_points
        }

    def _identify_challenges(self, content_lower: str) -> List[str]:
        """Identify challenges based on content analysis."""
        challenges = []
        challenge_keywords = {
            "requirement": "Clarifying project requirements and constraints",
            "constraint": "Clarifying project requirements and constraints",
            "balance": "Balancing competing design priorities",
            "trade": "Balancing competing design priorities",
            "sustain": "Integrating sustainable design principles",
            "green": "Integrating sustainable design principles",
            "budget": "Working within budget constraints",
            "cost": "Working within budget constraints",
            "time": "Managing project timeline effectively",
            "schedule": "Managing project timeline effectively",
            "client": "Addressing stakeholder needs and feedback",
            "stakeholder": "Addressing stakeholder needs and feedback"
        }
        for keyword, challenge in challenge_keywords.items():
            if keyword in content_lower and challenge not in challenges:
                challenges.append(challenge)
        if not challenges:
            challenges = [
                "Understanding project requirements and constraints",
                "Balancing functionality with aesthetic considerations",
                "Integrating sustainable design principles effectively"
            ]
        return challenges[:3]
    # def analyze_phase_progression(self, interactions: List[Dict]) -> Dict[str, Any]:
    #     """Analyze design phase progression from interactions."""
    #     if not interactions:
    #         return {
    #             "current_phase": "ideation",
    #             "phase_progress": 25,
    #             "session_duration": "Active",
    #             "challenges": [
    #                 "Understanding project requirements and constraints",
    #                 "Balancing functionality with aesthetic considerations",
    #                 "Integrating sustainable design principles effectively"
    #             ],
    #             "learning_points": [
    #                 "Developing systematic approach to design problems",
    #                 "Enhancing spatial reasoning and visualization skills",
    #                 "Improving design communication and presentation"
    #             ]
    #         }
        
    #     # Combine interaction content for analysis
    #     content_text = " ".join([
    #         str(i.get("data", {}).get("input", "")) + " " + 
    #         str(i.get("data", {}).get("response", "")) 
    #         for i in interactions
    #     ])
    #     content_lower = content_text.lower()
        
    #     # Calculate phase scores
    #     phase_scores = {}
    #     for phase, keywords in self.PHASE_KEYWORDS.items():
    #         score = sum(1 for keyword in keywords if keyword in content_lower)
    #         phase_scores[phase] = score
        
    #     # Determine current phase
    #     if phase_scores:
    #         current_phase = max(phase_scores, key=phase_scores.get)
    #         max_score = phase_scores[current_phase]
    #         total_possible = max(len(keywords) for keywords in self.PHASE_KEYWORDS.values())
    #         phase_progress = min((max_score / total_possible) * 100, 100) if total_possible > 0 else 0
    #     else:
    #         current_phase = "ideation"
    #         phase_progress = 0
        
    #     # Identify challenges based on content analysis
    #     challenges = self._identify_challenges(content_lower)
        
    #     # Identify learning points based on interaction patterns
    #     learning_points = self._identify_learning_points(content_lower, interactions)
        
    #     return {
    #         "current_phase": current_phase,
    #         "phase_progress": phase_progress,
    #         "session_duration": "Active" if len(interactions) > 0 else "New",
    #         "challenges": challenges,
    #         "learning_points": learning_points
    #     }
    
    # def _identify_challenges(self, content_lower: str) -> List[str]:
    #     """Identify challenges based on content analysis."""
    #     challenges = []
        
    #     challenge_keywords = {
    #         "requirement": "Clarifying project requirements and constraints",
    #         "constraint": "Clarifying project requirements and constraints",
    #         "balance": "Balancing competing design priorities",
    #         "trade": "Balancing competing design priorities",
    #         "sustain": "Integrating sustainable design principles",
    #         "green": "Integrating sustainable design principles",
    #         "budget": "Working within budget constraints",
    #         "cost": "Working within budget constraints",
    #         "time": "Managing project timeline effectively",
    #         "schedule": "Managing project timeline effectively",
    #         "client": "Addressing stakeholder needs and feedback",
    #         "stakeholder": "Addressing stakeholder needs and feedback"
    #     }
        
    #     for keyword, challenge in challenge_keywords.items():
    #         if keyword in content_lower and challenge not in challenges:
    #             challenges.append(challenge)
        
    #     # Default challenges if none detected
    #     if not challenges:
    #         challenges = [
    #             "Understanding project requirements and constraints",
    #             "Balancing functionality with aesthetic considerations",
    #             "Integrating sustainable design principles effectively"
    #         ]
        
    #     return challenges[:3]  # Return top 3 challenges
    
    def _identify_learning_points(self, content_lower: str, interactions: List[Dict]) -> List[str]:
        """Identify learning points based on interaction patterns."""
        learning_points = []
        
        learning_keywords = {
            "systematic": "Developing systematic approach to design problems",
            "spatial": "Enhancing spatial reasoning and visualization skills",
            "layout": "Enhancing spatial reasoning and visualization skills",
            "communicat": "Improving design communication and presentation",
            "present": "Improving design communication and presentation",
            "detail": "Understanding technical and construction details",
            "technical": "Understanding technical and construction details",
            "material": "Learning about material properties and applications",
            "finish": "Learning about material properties and applications",
            "light": "Integrating environmental and lighting considerations",
            "climate": "Integrating environmental and lighting considerations"
        }
        
        # Add learning points based on interaction count
        if len(interactions) > 5:
            learning_points.append("Developing systematic approach to design problems")
        
        for keyword, learning_point in learning_keywords.items():
            if keyword in content_lower and learning_point not in learning_points:
                learning_points.append(learning_point)
        
        # Default learning points if none detected
        if not learning_points:
            learning_points = [
                "Developing systematic approach to design problems",
                "Enhancing spatial reasoning and visualization skills",
                "Improving design communication and presentation"
            ]
        
        return learning_points[:3]  # Return top 3 learning points 