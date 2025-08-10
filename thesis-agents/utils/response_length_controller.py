# utils/response_length_controller.py - Response Length Control Utility

import re
from typing import Dict, Any, List
from config.user_experience_config import get_max_response_length

class ResponseLengthController:
    """Utility to control response length and formatting"""
    
    @staticmethod
    def truncate_response(response_text: str, agent_type: str = "default") -> str:
        """Truncate response to meet length limits with enhanced formatting"""
        
        max_length = get_max_response_length(agent_type)
        words = response_text.split()
        
        if len(words) <= max_length:
            return response_text
        
        # Truncate to max length with smart cutoff
        truncated_words = words[:max_length]
        truncated_response = " ".join(truncated_words)
        
        # Add ellipsis if truncated
        if len(words) > max_length:
            truncated_response += "..."
        
        # Clean up formatting
        truncated_response = re.sub(r'\n\s*\n\s*\n', '\n\n', truncated_response)
        truncated_response = truncated_response.strip()
        
        return truncated_response
    
    @staticmethod
    def remove_metrics_from_response(response_text: str) -> str:
        """Remove scientific metrics and technical details from response"""
        
        # Remove metrics sections - more comprehensive patterns
        patterns_to_remove = [
            # Main cognitive analysis sections
            r"🧠 COGNITIVE ANALYSIS & METHODOLOGY.*?(?=\n\n|\Z)",
            r"📊 SCIENTIFIC METRICS CALCULATION.*?(?=\n\n|\Z)",
            r"🔬 SCIENTIFIC METHODOLOGY.*?(?=\n\n|\Z)",
            r"🎯 PHASE-SPECIFIC ANALYSIS.*?(?=\n\n|\Z)",
            r"💡 RECOMMENDATIONS.*?(?=\n\n|\Z)",
            r"📚 RESEARCH BASIS.*?(?=\n\n|\Z)",
            r"Expected Outcomes.*?(?=\n\n|\Z)",
            
            # Individual metric lines
            r"Formula:.*?(?=\n|$)",
            r"Your Data:.*?(?=\n|$)",
            r"Target:.*?(?=\n|$)",
            r"Score:.*?(?=\n|$)",
            r"Calculation:.*?(?=\n|$)",
            r"Baseline:.*?(?=\n|$)",
            r"Improvement:.*?(?=\n|$)",
            r"Confidence:.*?(?=\n|$)",
            r"Detection Confidence:.*?(?=\n|$)",
            r"Current Phase:.*?(?=\n|$)",
            r"Focus:.*?(?=\n|$)",
            r"Cognitive Demands:.*?(?=\n|$)",
            r"Expected Duration:.*?(?=\n|$)",
            r"Success Indicators:.*?(?=\n|$)",
            r"Engagement:.*?(?=\n|$)",
            r"Complexity:.*?(?=\n|$)",
            r"Reflection:.*?(?=\n|$)",
            r"Overall Score:.*?(?=\n|$)",
            r"Improvement vs BASELINE:.*?(?=\n|$)",
            r"OVERALL COGNITIVE SCORE:.*?(?=\n|$)",
            r"📈 IMPROVEMENT vs BASELINE:.*?(?=\n|$)",
            r"🎯 OVERALL COGNITIVE SCORE:.*?(?=\n|$)",
            r"📊 Your Cognitive Profile:.*?(?=\n\n|\Z)",
            r"🎯 Key Insight:.*?(?=\n|$)",
            r"💡 Quick Tip:.*?(?=\n|$)",
            
            # Research and methodology sections
            r"This assessment uses evidence-based formulas.*?(?=\n\n|\Z)",
            r"\*This assessment uses evidence-based formulas\*.*?(?=\n\n|\Z)",
            r"\*This methodology is validated by:\*.*?(?=\n\n|\Z)",
            r"\*Expected Outcomes:\*.*?(?=\n\n|\Z)",
            r"\*Based on our benchmarking data\*.*?(?=\n\n|\Z)",
            
            # Additional cognitive analysis patterns
            r"• Average message length:.*?(?=\n|$)",
            r"• Engagement depth:.*?(?=\n|$)",
            r"• Recent engagement:.*?(?=\n|$)",
            r"• Vocabulary diversity:.*?(?=\n|$)",
            r"• Conceptual density:.*?(?=\n|$)",
            r"• Total words analyzed:.*?(?=\n|$)",
            r"• Metacognitive indicators:.*?(?=\n|$)",
            r"• Self-assessment indicators:.*?(?=\n|$)",
            r"• Complexity progression:.*?(?=\n|$)",
            r"• Early vs recent complexity:.*?(?=\n|$)",
            
            # Based on research patterns
            r"• Educational Psychology Research:.*?(?=\n|$)",
            r"• Design Thinking Studies:.*?(?=\n|$)",
            r"• Architectural Education:.*?(?=\n|$)",
            r"• Benchmarking Data:.*?(?=\n|$)",
            
            # Cognitive Load Theory and other research references
            r"• Cognitive Load Theory.*?(?=\n|$)",
            r"• Design Thinking Research.*?(?=\n|$)",
            r"• Metacognitive Development Studies.*?(?=\n|$)",
            r"• Architectural Education Benchmarks.*?(?=\n|$)",
            
            # Additional patterns to catch remaining pieces
            r"Current Design Phase:.*?(?=\n|$)",
            r"Detection Confidence:.*?(?=\n|$)",
            r"1\. Engagement Analysis.*?(?=\n|$)",
            r"2\. Complexity Analysis.*?(?=\n|$)",
            r"3\. Reflection Analysis.*?(?=\n|$)",
            r"4\. Progression Analysis.*?(?=\n|$)",
            r"🎯 OVERALL COGNITIVE.*?(?=\n|$)",
            r"Based on your cognitive profile:.*?(?=\n|$)",
            r"This methodology is validated by:.*?(?=\n|$)"
        ]
        
        cleaned_response = response_text
        
        for pattern in patterns_to_remove:
            cleaned_response = re.sub(pattern, "", cleaned_response, flags=re.DOTALL | re.IGNORECASE)
        
        # Clean up extra whitespace
        cleaned_response = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned_response)
        cleaned_response = cleaned_response.strip()
        
        return cleaned_response
    
    @staticmethod
    def format_cognitive_intervention(response_text: str, style: str = "friendly") -> str:
        """Format cognitive intervention based on style preference"""
        
        if style == "minimal":
            # Remove all formatting and keep only the core message
            response_text = re.sub(r'\*\*.*?\*\*', '', response_text)  # Remove bold
            response_text = re.sub(r'\*.*?\*', '', response_text)      # Remove italics
            response_text = re.sub(r'•\s*', '', response_text)         # Remove bullet points
            response_text = re.sub(r'🧠\s*', '', response_text)        # Remove emoji
            response_text = re.sub(r'\n\s*\n', '\n', response_text)    # Reduce spacing
        
        elif style == "academic":
            # Keep academic formatting but remove friendly elements
            response_text = re.sub(r'🧠\s*', '**Cognitive Enhancement:** ', response_text)
            response_text = re.sub(r'•\s*', '- ', response_text)
            response_text = re.sub(r'\*This helps.*?\*', '', response_text)
            response_text = re.sub(r'\*True expertise.*?\*', '', response_text)
            response_text = re.sub(r'\*Your unique.*?\*', '', response_text)
            response_text = re.sub(r'\*The goal is.*?\*', '', response_text)
        
        # Default is "friendly" - keep current formatting
        
        return response_text.strip()
    
    @staticmethod
    def ensure_response_quality(response_text: str, agent_type: str = "default") -> str:
        """Ensure response meets quality standards"""
        
        # Remove metrics if not supposed to show
        from config.user_experience_config import should_show_metrics
        if not should_show_metrics("cognitive_summary"):
            response_text = ResponseLengthController.remove_metrics_from_response(response_text)
        
        # Truncate if too long
        response_text = ResponseLengthController.truncate_response(response_text, agent_type)
        
        # Format cognitive interventions
        if "🧠" in response_text or "cognitive" in response_text.lower():
            from config.user_experience_config import get_cognitive_style
            style = get_cognitive_style()
            response_text = ResponseLengthController.format_cognitive_intervention(response_text, style)
        
        # Ensure proper ending on a sentence boundary
        cleaned = response_text.strip()
        # If truncated with ellipsis, prefer the last completed sentence
        if cleaned.endswith("..."):
            # Prefer ending at the last '.', '!' or '?'
            last_end = max(cleaned.rfind('.'), cleaned.rfind('!'), cleaned.rfind('?'))
            if last_end != -1:
                cleaned = cleaned[: last_end + 1]
        # If still not ending with sentence terminator, trim to last full sentence if possible
        if len(cleaned) > 0 and cleaned[-1] not in ".!?":
            last_end = max(cleaned.rfind('.'), cleaned.rfind('!'), cleaned.rfind('?'))
            if last_end != -1:
                cleaned = cleaned[: last_end + 1]
            else:
                # As a last resort, append a period to avoid trailing fragments
                cleaned = cleaned.rstrip() + "."
        response_text = cleaned

        # Readability polish: add gentle paragraph breaks between sentences
        import re as _re
        response_text = _re.sub(r'([.!?])\s+', r'\1\n\n', response_text).strip()

        # Normalize simple list markers into bullets
        response_text = _re.sub(r'(?m)^\s*(•|\-)\s*', '- ', response_text)

        # Normalize numbered lists to one-per-line structure for readability
        response_text = _re.sub(r'(?m)\s*(\d+)\.\s+', lambda m: f"\n{m.group(1)}. ", response_text)

        # Bold short heading-like lines that end with a colon
        response_text = _re.sub(r'(?m)^([A-Z][A-Za-z ]{2,40}):\s*$', r'**\1:**', response_text)
        
        return response_text.strip()
    
    @staticmethod
    def count_words(text: str) -> int:
        """Count words in text"""
        return len(text.split())
    
    @staticmethod
    def is_response_too_long(response_text: str, agent_type: str = "default") -> bool:
        """Check if response exceeds length limit"""
        word_count = ResponseLengthController.count_words(response_text)
        max_length = get_max_response_length(agent_type)
        return word_count > max_length

# Quick utility functions
def truncate_response(response_text: str, agent_type: str = "default") -> str:
    """Quick function to truncate response"""
    return ResponseLengthController.truncate_response(response_text, agent_type)

def remove_metrics(response_text: str) -> str:
    """Quick function to remove metrics"""
    return ResponseLengthController.remove_metrics_from_response(response_text)

def ensure_quality(response_text: str, agent_type: str = "default") -> str:
    """Quick function to ensure response quality"""
    return ResponseLengthController.ensure_response_quality(response_text, agent_type) 