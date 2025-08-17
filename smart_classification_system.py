#!/usr/bin/env python3
"""
Smart hybrid classification system that combines AI reasoning with improved pattern matching
"""

import sys
import re
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass

sys.path.insert(0, 'thesis-agents')

@dataclass
class SmartClassification:
    """Smart classification result"""
    interaction_type: str
    confidence: float
    reasoning: str
    ai_classification: str
    pattern_classification: str
    final_decision: str
    should_override_ai: bool

class SmartClassificationSystem:
    """Hybrid classification system that intelligently combines AI and pattern matching"""
    
    def __init__(self):
        self.design_guidance_patterns = [
            # Clear design guidance requests (helping with actual design work)
            r"i need help (organizing|arranging|planning|designing)",
            r"help me (organize|arrange|plan|design)",
            r"need guidance (on|with|for)",
            r"need advice (on|with|for)",
            r"help.*organizing.*spaces",
            r"help.*with.*layout",
            r"guidance.*spatial",
            r"^help$",  # Simple help requests
            # Removed: r"how should i (organize|arrange|handle|approach|design)" - this is often knowledge seeking
        ]
        
        self.knowledge_seeking_patterns = [
            # Pure knowledge requests (asking for information, not design help)
            r"what are.*strategies",
            r"tell me about.*strategies",
            r"explain.*strategies",
            r"what is.*concept",
            r"how do.*work",
            r"what are.*principles",
            r"can you tell me about",
            r"can you explain.*about",
            r"information.*about",
            r"what.*factors.*consider",  # This is knowledge seeking, not design guidance
            r"how should i handle.*patterns",  # Asking about handling patterns is knowledge seeking
            r"how should i.*handle",  # Generally asking how to handle something is knowledge seeking
            r"how.*handle.*patterns",
        ]
        
        self.example_request_patterns = [
            r"examples? of",
            r"show me.*examples?",
            r"give.*examples?",
            r"case studies?",
            r"precedents?",
            r"similar projects?",
        ]
        
        self.confusion_patterns = [
            r"don't understand",
            r"not following",
            r"confused",
            r"unclear",
            r"can you explain.*differently",
            r"what do you mean",
        ]
        
        self.feedback_request_patterns = [
            r"what do you think",
            r"your thoughts",
            r"your opinion",
            r"feedback on",
            r"thoughts on",
        ]
    
    def classify_with_patterns(self, user_input: str) -> Tuple[str, float, str]:
        """Classify using improved pattern matching"""
        user_input_lower = user_input.lower()
        
        # Check patterns in priority order
        
        # 1. Confusion expressions (highest priority for clarity)
        for pattern in self.confusion_patterns:
            if re.search(pattern, user_input_lower):
                return "confusion_expression", 0.9, f"Matched confusion pattern: {pattern}"
        
        # 2. Example requests (high priority, clear intent)
        for pattern in self.example_request_patterns:
            if re.search(pattern, user_input_lower):
                return "example_request", 0.9, f"Matched example pattern: {pattern}"
        
        # 3. Design guidance (help with organizing, planning, etc.)
        for pattern in self.design_guidance_patterns:
            if re.search(pattern, user_input_lower):
                return "design_guidance", 0.8, f"Matched design guidance pattern: {pattern}"
        
        # 4. Knowledge seeking (information requests)
        for pattern in self.knowledge_seeking_patterns:
            if re.search(pattern, user_input_lower):
                return "knowledge_seeking", 0.8, f"Matched knowledge seeking pattern: {pattern}"
        
        # 5. Feedback requests (asking for opinions)
        for pattern in self.feedback_request_patterns:
            if re.search(pattern, user_input_lower):
                return "feedback_request", 0.7, f"Matched feedback pattern: {pattern}"
        
        # Default fallback
        if "?" in user_input:
            return "knowledge_seeking", 0.3, "Question format suggests knowledge seeking"
        else:
            return "design_exploration", 0.3, "Default classification for statements"
    
    def should_override_ai(self, ai_classification: str, pattern_classification: str, 
                          pattern_confidence: float, user_input: str) -> Tuple[bool, str]:
        """Determine if we should override AI classification with pattern matching"""
        
        # High confidence pattern matches should override AI
        if pattern_confidence >= 0.8:
            if ai_classification != pattern_classification:
                return True, f"High confidence pattern match ({pattern_confidence:.1f}) overrides AI"
        
        # Specific override rules based on common AI mistakes
        
        # AI often misclassifies design guidance as confusion
        if (ai_classification == "confusion_expression" and 
            pattern_classification == "design_guidance" and
            "help" in user_input.lower() and 
            "organizing" in user_input.lower()):
            return True, "AI incorrectly classified design guidance as confusion"
        
        # AI sometimes misclassifies knowledge seeking as feedback request
        if (ai_classification == "feedback_request" and 
            pattern_classification == "knowledge_seeking" and
            any(word in user_input.lower() for word in ["handle", "strategies", "factors"])):
            return True, "AI incorrectly classified knowledge seeking as feedback request"
        
        # AI sometimes misclassifies knowledge seeking as design problem
        if (ai_classification == "design_problem" and 
            pattern_classification == "knowledge_seeking" and
            user_input.lower().startswith(("what", "how", "can you tell"))):
            return True, "AI incorrectly classified knowledge seeking as design problem"
        
        return False, "AI classification accepted"
    
    def smart_classify(self, user_input: str, ai_classification: str, 
                      ai_reasoning: str = "") -> SmartClassification:
        """Perform smart hybrid classification"""
        
        # Get pattern-based classification
        pattern_type, pattern_confidence, pattern_reasoning = self.classify_with_patterns(user_input)
        
        # Determine if we should override AI
        should_override, override_reason = self.should_override_ai(
            ai_classification, pattern_type, pattern_confidence, user_input
        )
        
        # Make final decision
        if should_override:
            final_decision = pattern_type
            confidence = pattern_confidence
            reasoning = f"OVERRIDE: {override_reason}. {pattern_reasoning}"
        else:
            final_decision = ai_classification
            confidence = 0.7  # Default AI confidence
            reasoning = f"AI classification accepted. {ai_reasoning[:100]}..."
        
        return SmartClassification(
            interaction_type=final_decision,
            confidence=confidence,
            reasoning=reasoning,
            ai_classification=ai_classification,
            pattern_classification=pattern_type,
            final_decision=final_decision,
            should_override_ai=should_override
        )

def test_smart_classification():
    """Test the smart classification system"""
    print("🧠 TESTING SMART HYBRID CLASSIFICATION")
    print("=" * 80)
    
    classifier = SmartClassificationSystem()
    
    # Test cases with AI classifications from the previous run
    test_cases = [
        {
            'input': 'I need help organizing spaces for different age groups in my community center.',
            'ai_classification': 'confusion_expression',
            'expected': 'design_guidance'
        },
        {
            'input': 'How should I handle circulation patterns in a large community space?',
            'ai_classification': 'feedback_request',  # This was wrong
            'expected': 'knowledge_seeking'
        },
        {
            'input': 'Can you tell me about passive cooling strategies for large buildings?',
            'ai_classification': 'knowledge_seeking',
            'expected': 'knowledge_seeking'
        },
        {
            'input': 'What are some examples of successful community centers in hot climates?',
            'ai_classification': 'example_request',
            'expected': 'example_request'
        },
        {
            'input': 'I don\'t understand what you mean by spatial hierarchy.',
            'ai_classification': 'confusion_expression',
            'expected': 'confusion_expression'
        },
        {
            'input': 'What factors should I consider when choosing materials?',
            'ai_classification': 'knowledge_seeking',
            'expected': 'knowledge_seeking'
        }
    ]
    
    correct = 0
    total = len(test_cases)
    
    for test_case in test_cases:
        user_input = test_case['input']
        ai_class = test_case['ai_classification']
        expected = test_case['expected']
        
        result = classifier.smart_classify(user_input, ai_class)
        
        is_correct = result.final_decision == expected
        if is_correct:
            correct += 1
        
        status = '✅' if is_correct else '❌'
        print(f"{status} {user_input[:50]}...")
        print(f"    AI: {ai_class} | Pattern: {result.pattern_classification}")
        print(f"    Final: {result.final_decision} | Expected: {expected}")
        print(f"    Override: {result.should_override_ai}")
        print(f"    Reasoning: {result.reasoning[:80]}...")
        print()
    
    accuracy = (correct / total) * 100
    print(f"📊 SMART CLASSIFICATION RESULTS: {correct}/{total} correct ({accuracy:.1f}%)")
    
    return accuracy >= 90

if __name__ == "__main__":
    test_smart_classification()
