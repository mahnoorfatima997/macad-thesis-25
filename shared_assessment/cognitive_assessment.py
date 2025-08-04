"""
Shared cognitive assessment functions for consistent evaluation across the system.
These functions analyze actual response content to determine cognitive metrics.
"""

from typing import Dict, List, Optional, Any


class CognitiveAssessment:
    """Real cognitive assessment based on response content analysis"""
    
    @staticmethod
    def assess_cognitive_offloading_prevention(response: str, response_type: str = "") -> bool:
        """
        Assess if response prevents cognitive offloading (KEY THESIS METRIC)
        
        Returns True if the response avoids giving direct answers and instead
        guides the student to think for themselves.
        """
        if not response:
            return False
            
        response_lower = response.lower()
        
        # Direct answers indicate cognitive offloading
        direct_answer_indicators = [
            "the answer is", "you should", "the correct", "simply do", "just use",
            "here's what you need", "the solution is", "follow these steps",
            "it is", "this means", "definitely", "obviously"
        ]
        
        has_direct_answers = any(indicator in response_lower for indicator in direct_answer_indicators)
        
        # Questions and challenges prevent offloading
        has_questions = "?" in response
        is_cognitive_challenge = response_type in ["cognitive_primary", "cognitive_integrated_socratic", "cognitive_challenge"]
        is_socratic = "socratic" in response_type.lower()
        
        # Guidance language that promotes thinking
        guidance_indicators = [
            "consider", "think about", "explore", "reflect", "what if",
            "how might", "why do you think", "what would happen",
            "can you", "have you considered", "let's examine"
        ]
        provides_guidance_not_solutions = any(word in response_lower for word in guidance_indicators)
        
        # Response prevents offloading if it guides without giving answers
        return (has_questions or is_cognitive_challenge or is_socratic or provides_guidance_not_solutions) and not has_direct_answers
    
    @staticmethod
    def assess_deep_thinking_encouragement(response: str) -> bool:
        """
        Assess if response encourages deep thinking (KEY THESIS METRIC)
        
        Returns True if the response promotes analysis, synthesis, evaluation,
        or other higher-order thinking skills.
        """
        if not response:
            return False
            
        response_lower = response.lower()
        
        deep_thinking_indicators = [
            "consider", "think about", "how might", "what if", "why do you think",
            "can you explain", "what factors", "how does this relate", "implications",
            "analyze", "evaluate", "compare", "synthesize", "reflect on",
            "examine", "investigate", "explore the relationship", "what patterns",
            "how would you approach", "what are the consequences", "justify",
            "critique", "assess", "interpret", "hypothesize"
        ]
        
        return any(indicator in response_lower for indicator in deep_thinking_indicators)
    
    @staticmethod
    def assess_scaffolding(response: str, cognitive_flags: List[str] = None) -> bool:
        """
        Assess if response provides appropriate scaffolding (KEY THESIS METRIC)
        
        Returns True if the response provides structured support that helps
        the student progress without doing the work for them.
        """
        if not response:
            return False
            
        response_lower = response.lower()
        
        # Good scaffolding addresses identified cognitive gaps
        addresses_gaps = cognitive_flags and len(cognitive_flags) > 0
        
        scaffolding_indicators = [
            "let's start with", "first consider", "one approach", "step by step",
            "building on", "similar to", "for example", "to help you think about",
            "break it down", "let's focus on", "begin by", "next, you might",
            "recall that", "remember when", "as we discussed", "connecting to"
        ]
        
        has_scaffolding_language = any(indicator in response_lower for indicator in scaffolding_indicators)
        
        # Check for progressive structure
        has_structure = any(marker in response_lower for marker in ["first", "then", "finally", "start", "next"])
        
        return has_scaffolding_language or has_structure or addresses_gaps
    
    @staticmethod
    def assess_engagement_maintenance(response: str, response_type: str = "") -> bool:
        """
        Assess if response maintains student engagement
        
        Returns True if the response uses engaging language or techniques
        that maintain student interest and motivation.
        """
        if not response:
            return False
            
        response_lower = response.lower()
        
        engagement_indicators = [
            "interesting", "fascinating", "what do you think", "your thoughts",
            "explore", "discover", "imagine", "picture this", "consider this",
            "curious", "wonder", "intriguing", "let's dive into", "exciting",
            "creative", "innovative", "your perspective", "share your ideas"
        ]
        
        is_engaging_type = response_type in ["socratic_primary", "cognitive_primary", "knowledge_enhanced_socratic"]
        has_engaging_language = any(indicator in response_lower for indicator in engagement_indicators)
        
        # Questions are inherently engaging
        has_questions = "?" in response
        
        return is_engaging_type or has_engaging_language or has_questions
    
    @staticmethod
    def assess_skill_adaptation(response: str, skill_level: str, input_complexity: float = 0.5) -> bool:
        """
        Assess if response adapts to student skill level
        
        Returns True if the response complexity matches the student's level.
        """
        if not response:
            return False
            
        response_complexity = CognitiveAssessment._estimate_response_complexity(response)
        
        # Check if complexity matches skill level
        if skill_level == "beginner":
            # Simple responses for beginners
            return response_complexity <= 0.5 and input_complexity <= 0.6
        elif skill_level == "intermediate":
            # Moderate complexity for intermediate
            return 0.3 <= response_complexity <= 0.8
        elif skill_level == "advanced":
            # Complex responses for advanced
            return response_complexity >= 0.5
        
        return True  # Default to appropriate
    
    @staticmethod
    def _estimate_response_complexity(response: str) -> float:
        """Estimate complexity of response (0-1 scale)"""
        if not response:
            return 0.0
            
        words = response.split()
        if not words:
            return 0.0
            
        # Average word length
        avg_word_length = sum(len(word) for word in words) / len(words)
        
        # Technical architectural terms
        technical_terms = [
            "accessibility", "circulation", "program", "zoning", "egress", 
            "fenestration", "massing", "parti", "typology", "vernacular",
            "articulation", "threshold", "porosity", "tectonics", "materiality",
            "phenomenology", "morphology", "syntax", "precedent", "iteration"
        ]
        technical_count = sum(1 for term in technical_terms if term in response.lower())
        
        # Sentence complexity (words per sentence)
        sentences = response.split('.')
        avg_sentence_length = len(words) / max(len(sentences), 1)
        
        # Normalize complexity (0-1)
        word_complexity = min(avg_word_length / 8, 1.0)
        technical_complexity = min(technical_count / 5, 1.0)
        sentence_complexity = min(avg_sentence_length / 20, 1.0)
        
        # Weighted average
        complexity = (word_complexity * 0.3 + technical_complexity * 0.4 + sentence_complexity * 0.3)
        
        return min(complexity, 1.0)
    
    @staticmethod
    def calculate_composite_scores(
        prevents_offloading: bool,
        encourages_thinking: bool,
        provides_scaffolding: bool,
        maintains_engagement: bool,
        adapts_to_skill: bool
    ) -> Dict[str, float]:
        """
        Calculate composite cognitive enhancement scores
        
        Returns a dictionary of normalized scores (0-1 scale)
        """
        # Convert booleans to floats
        scores = {
            'cognitive_offloading_prevention': float(prevents_offloading),
            'deep_thinking_encouragement': float(encourages_thinking),
            'scaffolding_effectiveness': float(provides_scaffolding),
            'engagement_maintenance': float(maintains_engagement),
            'skill_adaptation': float(adapts_to_skill)
        }
        
        # Calculate composite score (weighted average)
        weights = {
            'cognitive_offloading_prevention': 0.3,  # Highest weight - core thesis metric
            'deep_thinking_encouragement': 0.3,      # Highest weight - core thesis metric
            'scaffolding_effectiveness': 0.2,
            'engagement_maintenance': 0.1,
            'skill_adaptation': 0.1
        }
        
        composite_score = sum(scores[key] * weights[key] for key in scores)
        scores['composite_cognitive_score'] = round(composite_score, 3)
        
        return scores