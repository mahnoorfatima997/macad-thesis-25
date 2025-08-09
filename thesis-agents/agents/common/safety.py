"""
Shared safety validation utilities for agents.
"""

import re
from typing import List, Dict, Any, Tuple


class SafetyValidator:
    """
    Shared safety validation utilities for content filtering and validation.
    """
    
    # Common unsafe patterns to check for
    UNSAFE_PATTERNS = [
        r'\b(hack|exploit|bypass|jailbreak)\b',
        r'\b(harmful|dangerous|illegal)\b',
        r'\b(violence|violent|attack)\b'
    ]
    
    # Educational content indicators (safe)
    EDUCATIONAL_PATTERNS = [
        r'\b(learn|study|understand|explain|teach)\b',
        r'\b(architecture|design|building|construction)\b',
        r'\b(academic|educational|thesis|research)\b'
    ]
    
    @classmethod
    def validate_content(cls, content: str) -> Tuple[bool, List[str]]:
        """
        Validate content for safety and educational appropriateness.
        
        Args:
            content: Content to validate
            
        Returns:
            Tuple of (is_safe, list_of_issues)
        """
        issues = []
        content_lower = content.lower()
        
        # Check for unsafe patterns
        for pattern in cls.UNSAFE_PATTERNS:
            if re.search(pattern, content_lower, re.IGNORECASE):
                issues.append(f"Potentially unsafe content detected: {pattern}")
        
        # Check content length
        if len(content) > 10000:
            issues.append("Content exceeds safe length limit")
        
        # Check for excessive repetition
        if cls._has_excessive_repetition(content):
            issues.append("Excessive repetition detected")
        
        is_safe = len(issues) == 0
        return is_safe, issues
    
    @classmethod
    def validate_response_appropriateness(cls, response: str, context: str = "") -> bool:
        """
        Validate if a response is appropriate for educational context.
        
        Args:
            response: Response to validate
            context: Optional context for validation
            
        Returns:
            True if appropriate, False otherwise
        """
        # Check basic safety
        is_safe, _ = cls.validate_content(response)
        if not is_safe:
            return False
        
        # Check if response is educational/helpful
        response_lower = response.lower()
        has_educational_content = any(
            re.search(pattern, response_lower, re.IGNORECASE) 
            for pattern in cls.EDUCATIONAL_PATTERNS
        )
        
        # Check response isn't too vague
        if len(response.strip()) < 20:
            return False
        
        return has_educational_content or "architecture" in context.lower()
    
    @classmethod
    def _has_excessive_repetition(cls, text: str) -> bool:
        """Check if text has excessive repetition."""
        words = text.lower().split()
        if len(words) < 10:
            return False
        
        # Check for repeated phrases
        word_counts = {}
        for word in words:
            word_counts[word] = word_counts.get(word, 0) + 1
        
        # If any single word appears more than 20% of the time, it's excessive
        max_count = max(word_counts.values())
        return max_count > len(words) * 0.2
    
    @classmethod
    def sanitize_input(cls, user_input: str) -> str:
        """
        Sanitize user input by removing potentially problematic content.
        
        Args:
            user_input: Raw user input
            
        Returns:
            Sanitized input
        """
        # Remove excessive whitespace
        sanitized = re.sub(r'\s+', ' ', user_input.strip())
        
        # Remove potential injection patterns
        sanitized = re.sub(r'[<>{}]', '', sanitized)
        
        # Truncate if too long
        if len(sanitized) > 2000:
            sanitized = sanitized[:2000] + "..."
        
        return sanitized
    
    @classmethod
    def check_prompt_injection(cls, input_text: str) -> bool:
        """
        Check for potential prompt injection attempts.
        
        Args:
            input_text: Text to check
            
        Returns:
            True if potential injection detected
        """
        injection_patterns = [
            r'ignore\s+previous\s+instructions',
            r'system\s*:',
            r'assistant\s*:',
            r'you\s+are\s+now',
            r'forget\s+everything',
            r'new\s+instructions'
        ]
        
        text_lower = input_text.lower()
        return any(re.search(pattern, text_lower) for pattern in injection_patterns) 