"""
Content processing module for formatting, validation, and optimization of knowledge content.
"""
from typing import Dict, Any, List, Optional
from ...common import TextProcessor, MetricsCalculator, AgentTelemetry


class ContentProcessingProcessor:
    """
    Processes content formatting, validation, and optimization.
    """
    
    def __init__(self):
        self.telemetry = AgentTelemetry("content_processing")
        self.text_processor = TextProcessor()
        self.metrics_calculator = MetricsCalculator()
        
    def format_examples_list(self, examples: List[str]) -> str:
        """Format examples into a readable list."""
        try:
            if not examples:
                return "No specific examples available at this time."
            
            formatted = "Examples:\n"
            for i, example in enumerate(examples[:5], 1):
                # Clean and format each example
                clean_example = self._clean_example_text(example)
                formatted += f"{i}. {clean_example}\n"
            
            return formatted.strip()
            
        except Exception as e:
            self.telemetry.log_error("format_examples_list", str(e))
            return "Examples are available for this topic."
    
    def enhance_search_results(self, results: List[Dict], context: Dict) -> List[Dict]:
        """Enhance search results with additional context."""
        try:
            enhanced_results = []
            
            for result in results:
                enhanced_result = result.copy()
                
                # Add context relevance score
                relevance_score = self._calculate_context_relevance(result, context)
                enhanced_result['context_relevance'] = relevance_score
                
                # Enhance snippet with formatting
                snippet = result.get('snippet', '')
                enhanced_result['formatted_snippet'] = self._format_snippet(snippet)
                
                # Add architectural keywords
                enhanced_result['architectural_keywords'] = self._extract_architectural_keywords(result)
                
                # Add content type classification
                enhanced_result['content_type'] = self._classify_content_type(result)
                
                enhanced_results.append(enhanced_result)
            
            # Sort by context relevance
            enhanced_results.sort(key=lambda x: x.get('context_relevance', 0), reverse=True)
            
            return enhanced_results
            
        except Exception as e:
            self.telemetry.log_error("enhance_search_results", str(e))
            return results
    
    def validate_response_completeness(self, response: Dict[str, Any]) -> bool:
        """Validate if response is complete and informative."""
        try:
            completeness_checks = []
            
            # Check main content
            main_content = response.get('main_content', '')
            if main_content and len(main_content) > 50:
                completeness_checks.append(True)
            else:
                completeness_checks.append(False)
            
            # Check for examples or key points
            examples = response.get('examples', [])
            key_points = response.get('key_points', [])
            if examples or key_points:
                completeness_checks.append(True)
            else:
                completeness_checks.append(False)
            
            # Check for educational value
            educational_content = response.get('educational_response', '')
            if educational_content and len(educational_content) > 100:
                completeness_checks.append(True)
            else:
                completeness_checks.append(False)
            
            # Response is complete if at least 2/3 checks pass
            return sum(completeness_checks) >= 2
            
        except Exception as e:
            self.telemetry.log_error("validate_response_completeness", str(e))
            return False
    
    def optimize_for_learning(self, content: str, user_level: str = 'intermediate') -> str:
        """Optimize content for learning based on user level."""
        try:
            if not content:
                return "Content is being prepared for your learning level."
            
            optimized_content = content
            
            if user_level == 'beginner':
                # Add introductory context
                if not self._has_introductory_context(content):
                    optimized_content = self._add_introductory_context(content)
                
                # Simplify technical terms
                optimized_content = self._simplify_technical_terms(optimized_content)
                
                # Add basic explanations
                optimized_content = self._add_basic_explanations(optimized_content)
                
            elif user_level == 'advanced':
                # Add technical depth
                optimized_content = self._add_technical_depth(content)
                
                # Include advanced considerations
                optimized_content = self._add_advanced_considerations(content)
                
            # Ensure proper structure
            optimized_content = self._ensure_proper_structure(optimized_content)
            
            return optimized_content
            
        except Exception as e:
            self.telemetry.log_error("optimize_for_learning", str(e))
            return content
    
    def finalize_knowledge_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Finalize knowledge response with proper formatting and validation."""
        try:
            finalized_response = response_data.copy()
            
            # Ensure main content is properly formatted
            main_content = finalized_response.get('main_content', '')
            if main_content:
                finalized_response['main_content'] = self._format_main_content(main_content)
            
            # Format examples
            examples = finalized_response.get('examples', [])
            if examples:
                finalized_response['formatted_examples'] = self.format_examples_list(examples)
            
            # Add response metadata
            finalized_response['response_quality'] = self._assess_response_quality(finalized_response)
            finalized_response['word_count'] = self._calculate_word_count(finalized_response)
            finalized_response['readability_score'] = self._assess_readability(finalized_response)
            
            # Add completion timestamp
            finalized_response['finalized_at'] = self.telemetry.get_timestamp()
            
            return finalized_response
            
        except Exception as e:
            self.telemetry.log_error("finalize_knowledge_response", str(e))
            return response_data
    
    def track_knowledge_usage(self, topic: str, results_count: int, user_context: Dict = None) -> None:
        """Track knowledge usage for analytics and optimization."""
        try:
            usage_data = {
                'topic': topic,
                'results_count': results_count,
                'timestamp': self.telemetry.get_timestamp()
            }
            
            # Add user context if available
            if user_context:
                usage_data.update({
                    'building_type': user_context.get('building_type', 'unknown'),
                    'complexity_level': user_context.get('complexity_level', 'unknown'),
                    'user_intent': user_context.get('user_intent', 'unknown')
                })
            
            # Log for analytics
            self.telemetry.log_metric("knowledge_usage", usage_data)
            
        except Exception as e:
            self.telemetry.log_error("track_knowledge_usage", str(e))
    
    # Helper methods for content processing
    
    def _calculate_context_relevance(self, result: Dict, context: Dict) -> float:
        """Calculate how relevant a result is to the given context."""
        try:
            relevance_score = 0.0
            
            title = result.get('title', '').lower()
            snippet = result.get('snippet', '').lower()
            
            # Building type relevance
            building_type = context.get('building_type', '')
            if building_type and building_type != 'general':
                if building_type in title or building_type in snippet:
                    relevance_score += 0.3
            
            # Topic focus relevance
            topic_focus = context.get('topic_focus', '')
            if topic_focus:
                focus_keywords = topic_focus.split('_')
                for keyword in focus_keywords:
                    if keyword in title or keyword in snippet:
                        relevance_score += 0.2
            
            # Complexity level match
            complexity_level = context.get('complexity_level', 'intermediate')
            if complexity_level == 'beginner':
                beginner_terms = ['basic', 'introduction', 'guide', 'fundamentals']
                if any(term in title or term in snippet for term in beginner_terms):
                    relevance_score += 0.2
            elif complexity_level == 'advanced':
                advanced_terms = ['advanced', 'complex', 'detailed', 'technical']
                if any(term in title or term in snippet for term in advanced_terms):
                    relevance_score += 0.2
            
            # Base relevance for architectural content
            arch_terms = ['architecture', 'design', 'building', 'construction']
            if any(term in title or term in snippet for term in arch_terms):
                relevance_score += 0.1
            
            return min(relevance_score, 1.0)
            
        except Exception as e:
            self.telemetry.log_error("_calculate_context_relevance", str(e))
            return 0.5
    
    def _format_snippet(self, snippet: str) -> str:
        """Format snippet for better readability."""
        if not snippet:
            return ""
        
        # Clean up snippet
        formatted = snippet.strip()
        
        # Ensure proper sentence structure
        if not formatted.endswith(('.', '!', '?')):
            formatted += "..."
        
        # Capitalize first letter
        if formatted and formatted[0].islower():
            formatted = formatted[0].upper() + formatted[1:]
        
        return formatted
    
    def _extract_architectural_keywords(self, result: Dict) -> List[str]:
        """Extract architectural keywords from result."""
        architectural_terms = [
            'architecture', 'design', 'building', 'construction', 'structural',
            'sustainable', 'planning', 'materials', 'engineering', 'aesthetic',
            'functional', 'space', 'environment', 'systems', 'performance'
        ]
        
        title = result.get('title', '').lower()
        snippet = result.get('snippet', '').lower()
        
        found_keywords = []
        for term in architectural_terms:
            if term in title or term in snippet:
                found_keywords.append(term)
        
        return found_keywords[:5]  # Return top 5 keywords
    
    def _classify_content_type(self, result: Dict) -> str:
        """Classify the type of content in the result."""
        title = result.get('title', '').lower()
        snippet = result.get('snippet', '').lower()
        
        # Classification patterns
        if any(word in title or word in snippet for word in ['guide', 'how to', 'tutorial']):
            return 'instructional'
        elif any(word in title or word in snippet for word in ['case', 'example', 'project']):
            return 'case_study'
        elif any(word in title or word in snippet for word in ['theory', 'principle', 'concept']):
            return 'theoretical'
        elif any(word in title or word in snippet for word in ['specification', 'standard', 'code']):
            return 'technical'
        elif any(word in title or word in snippet for word in ['news', 'trend', 'innovation']):
            return 'current_trends'
        else:
            return 'general'
    
    def _clean_example_text(self, example: str) -> str:
        """Clean and format example text."""
        if not example:
            return "Example not available"
        
        # Remove excessive whitespace
        cleaned = ' '.join(example.split())
        
        # Ensure reasonable length
        if len(cleaned) > 150:
            cleaned = cleaned[:147] + "..."
        
        # Ensure proper capitalization
        if cleaned and cleaned[0].islower():
            cleaned = cleaned[0].upper() + cleaned[1:]
        
        return cleaned
    
    def _has_introductory_context(self, content: str) -> bool:
        """Check if content has introductory context."""
        intro_indicators = ['introduction', 'overview', 'fundamentals', 'basics', 'what is']
        content_lower = content.lower()
        return any(indicator in content_lower for indicator in intro_indicators)
    
    def _add_introductory_context(self, content: str) -> str:
        """Add introductory context for beginners."""
        intro = "To understand this architectural concept, it's important to start with the fundamentals. "
        return intro + content
    
    def _simplify_technical_terms(self, content: str) -> str:
        """Simplify technical terms for beginners."""
        # Simple term replacements
        replacements = {
            'specification': 'detailed requirement',
            'optimization': 'improvement',
            'integration': 'combination',
            'implementation': 'putting into practice'
        }
        
        simplified = content
        for technical, simple in replacements.items():
            simplified = simplified.replace(technical, simple)
        
        return simplified
    
    def _add_basic_explanations(self, content: str) -> str:
        """Add basic explanations for complex concepts."""
        if 'sustainable' in content.lower() and 'sustainability' not in content.lower():
            content += "\n\nSustainability in architecture means designing buildings that are environmentally friendly and energy efficient."
        
        return content
    
    def _add_technical_depth(self, content: str) -> str:
        """Add technical depth for advanced users."""
        if len(content) < 300:
            content += "\n\nFor advanced implementation, consider the technical specifications, performance criteria, and integration requirements with other building systems."
        
        return content
    
    def _add_advanced_considerations(self, content: str) -> str:
        """Add advanced considerations."""
        content += "\n\nAdvanced practitioners should also consider long-term performance implications, maintenance requirements, and potential for future adaptations."
        return content
    
    def _ensure_proper_structure(self, content: str) -> str:
        """Ensure content has proper structure."""
        # Add paragraph breaks for long content
        if len(content) > 400 and '\n\n' not in content:
            # Find natural break points
            sentences = content.split('. ')
            if len(sentences) > 3:
                mid_point = len(sentences) // 2
                restructured = '. '.join(sentences[:mid_point]) + '.\n\n' + '. '.join(sentences[mid_point:])
                return restructured
        
        return content
    
    def _format_main_content(self, content: str) -> str:
        """Format main content for presentation."""
        if not content:
            return ""
        
        # Ensure proper paragraph structure
        formatted = content.replace('\n\n\n', '\n\n')
        
        # Ensure proper ending
        if not formatted.endswith(('.', '!', '?')):
            formatted += "."
        
        return formatted
    
    def _assess_response_quality(self, response: Dict[str, Any]) -> str:
        """Assess overall quality of response."""
        quality_factors = []
        
        # Content length
        main_content = response.get('main_content', '')
        if len(main_content) > 200:
            quality_factors.append('comprehensive')
        
        # Examples present
        if response.get('examples') or response.get('formatted_examples'):
            quality_factors.append('examples_included')
        
        # Educational value
        if response.get('educational_response'):
            quality_factors.append('educational')
        
        # Multiple sources
        if response.get('source_count', 0) > 2:
            quality_factors.append('well_sourced')
        
        if len(quality_factors) >= 3:
            return 'high'
        elif len(quality_factors) >= 2:
            return 'medium'
        else:
            return 'basic'
    
    def _calculate_word_count(self, response: Dict[str, Any]) -> int:
        """Calculate total word count of response."""
        total_words = 0
        
        # Count words in main content
        main_content = response.get('main_content', '')
        total_words += len(main_content.split())
        
        # Count words in educational response
        educational_response = response.get('educational_response', '')
        total_words += len(educational_response.split())
        
        # Count words in examples
        examples = response.get('examples', [])
        for example in examples:
            if isinstance(example, str):
                total_words += len(example.split())
        
        return total_words
    
    def _assess_readability(self, response: Dict[str, Any]) -> str:
        """Assess readability of response content."""
        main_content = response.get('main_content', '')
        
        if not main_content:
            return 'unknown'
        
        # Simple readability assessment based on sentence length
        sentences = main_content.split('.')
        if not sentences:
            return 'unknown'
        
        avg_sentence_length = sum(len(sentence.split()) for sentence in sentences) / len(sentences)
        
        if avg_sentence_length < 15:
            return 'easy'
        elif avg_sentence_length < 25:
            return 'moderate'
        else:
            return 'complex' 