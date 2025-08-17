"""
Shared text processing utilities for agents.
"""

import re
import random
from typing import List, Dict, Any


class TextProcessor:
    """
    Shared text processing utilities used across multiple agents.
    """
    
    @staticmethod
    def extract_indicators(text: str, indicators: List[str]) -> int:
        """
        Count occurrences of indicators in text (case-insensitive).
        
        Args:
            text: Text to search
            indicators: List of indicator phrases
            
        Returns:
            Count of indicator matches
        """
        text_lower = text.lower()
        return sum(1 for phrase in indicators if phrase in text_lower)

    @staticmethod
    def select_random(items: List[str]) -> str:
        """
        Select a random item from a list.

        Args:
            items: List of items to choose from

        Returns:
            Random item from the list, or empty string if list is empty
        """
        if not items:
            return ""
        return random.choice(items)
    
    @staticmethod
    def calculate_complexity_score(text: str) -> Dict[str, float]:
        """
        Calculate text complexity metrics.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with complexity metrics
        """
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        
        # Filter out empty sentences
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not words or not sentences:
            return {
                "avg_sentence_length": 0.0,
                "word_count": 0,
                "sentence_count": 0,
                "complexity_score": 0.0
            }
        
        avg_sentence_length = len(words) / len(sentences)
        
        # Simple complexity heuristic
        complexity_score = min(avg_sentence_length / 20.0, 1.0)  # Normalize to 0-1
        
        return {
            "avg_sentence_length": avg_sentence_length,
            "word_count": len(words),
            "sentence_count": len(sentences),
            "complexity_score": complexity_score
        }
    
    @staticmethod
    def extract_technical_terms(text: str, term_categories: Dict[str, List[str]]) -> Dict[str, int]:
        """
        Extract and count technical terms by category.
        
        Args:
            text: Text to analyze
            term_categories: Dictionary mapping categories to term lists
            
        Returns:
            Dictionary with counts per category
        """
        text_lower = text.lower()
        results = {}
        
        for category, terms in term_categories.items():
            count = sum(1 for term in terms if term in text_lower)
            results[category] = count
        
        return results
    
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean text by removing extra whitespace and normalizing.
        
        Args:
            text: Text to clean
            
        Returns:
            Cleaned text
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?-]', '', text)
        
        return text
    
    @staticmethod
    def extract_questions(text: str) -> List[str]:
        """
        Extract questions from text.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of questions found
        """
        # Split by sentence and find those ending with ?
        sentences = re.split(r'[.!?]+', text)
        questions = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and ('?' in sentence or 
                           sentence.lower().startswith(('what', 'how', 'why', 'when', 'where', 'who'))):
                questions.append(sentence)
        
        return questions
    
    @staticmethod
    def truncate_text(text: str, max_length: int, preserve_words: bool = True) -> str:
        """
        Truncate text to maximum length.
        
        Args:
            text: Text to truncate
            max_length: Maximum character length
            preserve_words: Whether to preserve word boundaries
            
        Returns:
            Truncated text
        """
        if len(text) <= max_length:
            return text
        
        if preserve_words:
            # Find last complete word within limit
            truncated = text[:max_length]
            last_space = truncated.rfind(' ')
            if last_space > max_length * 0.8:  # If we can preserve most of the text
                return truncated[:last_space] + "..."
        
        return text[:max_length-3] + "..." 