"""
Content analysis processing module for analyzing content depth and extracting technical information.
"""
from typing import Dict, Any, List, Optional
from ..schemas import ContentAnalysis
from ...common import TextProcessor, MetricsCalculator, AgentTelemetry
from state_manager import ArchMentorState


class ContentAnalysisProcessor:
    """
    Processes content analysis including technical term extraction and complexity assessment.
    """
    
    def __init__(self):
        self.telemetry = AgentTelemetry("content_analysis")
        self.text_processor = TextProcessor()
        self.metrics_calculator = MetricsCalculator()
        
    def perform_content_analysis(self, input_text: str, state: ArchMentorState) -> ContentAnalysis:
        """
        Perform comprehensive content analysis of student input.
        """
        self.telemetry.log_agent_start("perform_content_analysis")
        
        try:
            # Extract technical terms
            technical_terms = self._extract_technical_terms(input_text)
            
            # Extract emotional indicators
            emotional_indicators = self._extract_emotional_indicators(input_text)
            
            # Assess complexity and specificity
            complexity_score = self._assess_complexity(input_text)
            specificity_score = self._assess_specificity(input_text, state)
            
            # Extract key topics
            key_topics = self._extract_key_topics(input_text)
            
            # Analyze content structure
            content_structure = self._analyze_content_structure(input_text)
            
            # Assess content quality
            content_quality = self._assess_content_quality(input_text)
            
            # Extract domain-specific concepts
            domain_concepts = self._extract_domain_concepts(input_text)
            
            # Assess information density
            information_density = self._assess_information_density(input_text)
            
            analysis = ContentAnalysis(
                technical_terms=technical_terms,
                emotional_indicators=emotional_indicators,
                complexity_score=complexity_score,
                specificity_score=specificity_score,
                key_topics=key_topics,
                content_structure=content_structure,
                content_quality=content_quality,
                domain_concepts=domain_concepts,
                information_density=information_density,
                analysis_confidence=self._calculate_analysis_confidence(
                    technical_terms, complexity_score, specificity_score, content_quality
                )
            )
            
            self.telemetry.log_agent_end("perform_content_analysis")
            return analysis
            
        except Exception as e:
            self.telemetry.log_error("perform_content_analysis", str(e))
            return self._get_fallback_content_analysis()
    
    def _extract_technical_terms(self, input_text: str) -> List[str]:
        """Extract architectural and technical terms from input."""
        try:
            # Comprehensive list of architectural and technical terms
            architectural_terms = [
                # Structural terms
                'beam', 'column', 'foundation', 'slab', 'wall', 'roof', 'truss', 'joist',
                'lintel', 'cantilever', 'span', 'load', 'stress', 'compression', 'tension',
                'shear', 'moment', 'deflection', 'buckling',
                
                # Materials
                'concrete', 'steel', 'timber', 'wood', 'brick', 'stone', 'glass', 'aluminum',
                'composite', 'reinforcement', 'rebar', 'aggregate', 'cement', 'mortar',
                
                # Building systems
                'hvac', 'plumbing', 'electrical', 'lighting', 'ventilation', 'heating',
                'cooling', 'insulation', 'waterproofing', 'drainage',
                
                # Design concepts
                'sustainability', 'accessibility', 'circulation', 'orientation', 'zoning',
                'programming', 'massing', 'scale', 'proportion', 'rhythm', 'balance',
                'hierarchy', 'transparency', 'permeability',
                
                # Construction terms
                'excavation', 'formwork', 'curing', 'finishing', 'cladding', 'facade',
                'envelope', 'assembly', 'detail', 'connection', 'joint', 'sealant',
                
                # Codes and standards
                'building code', 'zoning', 'setback', 'fire rating', 'egress', 'ada',
                'accessibility', 'seismic', 'wind load', 'snow load'
            ]
            
            input_lower = input_text.lower()
            found_terms = []
            
            for term in architectural_terms:
                if term in input_lower:
                    found_terms.append(term)
            
            # Also look for compound technical terms
            compound_terms = self._extract_compound_technical_terms(input_text)
            found_terms.extend(compound_terms)
            
            # Remove duplicates while preserving order
            unique_terms = []
            seen = set()
            for term in found_terms:
                if term not in seen:
                    unique_terms.append(term)
                    seen.add(term)
            
            return unique_terms[:10]  # Return top 10 terms
            
        except Exception as e:
            self.telemetry.log_error("_extract_technical_terms", str(e))
            return []
    
    def _extract_emotional_indicators(self, input_text: str) -> Dict[str, int]:
        """Extract emotional indicators from input text."""
        try:
            emotional_categories = {
                'positive': [
                    'excited', 'happy', 'enthusiastic', 'interested', 'curious', 'motivated',
                    'confident', 'pleased', 'satisfied', 'inspired', 'amazed', 'wonderful',
                    'great', 'excellent', 'fantastic', 'love', 'enjoy', 'appreciate'
                ],
                'negative': [
                    'frustrated', 'confused', 'worried', 'concerned', 'disappointed', 'upset',
                    'anxious', 'stressed', 'overwhelmed', 'difficult', 'hard', 'challenging',
                    'hate', 'dislike', 'boring', 'tedious', 'annoying'
                ],
                'uncertain': [
                    'unsure', 'doubtful', 'hesitant', 'uncertain', 'maybe', 'perhaps',
                    'not sure', 'don\'t know', 'confused', 'unclear', 'ambiguous'
                ],
                'neutral': [
                    'okay', 'fine', 'alright', 'reasonable', 'acceptable', 'standard',
                    'normal', 'typical', 'usual', 'regular'
                ]
            }
            
            input_lower = input_text.lower()
            emotional_counts = {}
            
            for category, indicators in emotional_categories.items():
                count = sum(1 for indicator in indicators if indicator in input_lower)
                emotional_counts[category] = count
            
            return emotional_counts
            
        except Exception as e:
            self.telemetry.log_error("_extract_emotional_indicators", str(e))
            return {'positive': 0, 'negative': 0, 'uncertain': 0, 'neutral': 0}
    
    def _assess_complexity(self, input_text: str) -> float:
        """Assess the complexity of the input text."""
        try:
            complexity_factors = []
            
            # Lexical complexity (word length and variety)
            words = input_text.split()
            if words:
                avg_word_length = sum(len(word) for word in words) / len(words)
                unique_words = len(set(word.lower() for word in words))
                lexical_diversity = unique_words / len(words) if words else 0
                
                complexity_factors.append(min(avg_word_length / 6.0, 1.0))  # Normalize to 0-1
                complexity_factors.append(lexical_diversity)
            
            # Syntactic complexity (sentence structure)
            sentences = [s.strip() for s in input_text.split('.') if s.strip()]
            if sentences:
                avg_sentence_length = sum(len(sentence.split()) for sentence in sentences) / len(sentences)
                complexity_factors.append(min(avg_sentence_length / 20.0, 1.0))  # Normalize to 0-1
            
            # Technical term density
            technical_terms = self._extract_technical_terms(input_text)
            word_count = len(words) if words else 1
            technical_density = len(technical_terms) / word_count
            complexity_factors.append(min(technical_density * 10, 1.0))  # Scale and normalize
            
            # Conceptual complexity indicators
            complex_concepts = [
                'integration', 'synthesis', 'optimization', 'methodology', 'framework',
                'systematic', 'comprehensive', 'interdisciplinary', 'holistic', 'paradigm'
            ]
            input_lower = input_text.lower()
            concept_count = sum(1 for concept in complex_concepts if concept in input_lower)
            conceptual_complexity = min(concept_count / 3.0, 1.0)
            complexity_factors.append(conceptual_complexity)
            
            return sum(complexity_factors) / len(complexity_factors) if complexity_factors else 0.5
            
        except Exception as e:
            self.telemetry.log_error("_assess_complexity", str(e))
            return 0.5
    
    def _assess_specificity(self, input_text: str, state: ArchMentorState) -> float:
        """Assess how specific the input is."""
        try:
            specificity_factors = []
            
            # Specific architectural terms
            specific_terms = [
                'cantilever beam', 'reinforced concrete', 'curtain wall', 'green roof',
                'passive solar', 'thermal bridge', 'vapor barrier', 'fire separation',
                'seismic design', 'wind load', 'moment frame', 'shear wall'
            ]
            
            input_lower = input_text.lower()
            specific_term_count = sum(1 for term in specific_terms if term in input_lower)
            specificity_factors.append(min(specific_term_count / 2.0, 1.0))
            
            # Numerical specificity (measurements, quantities, etc.)
            import re
            numbers = re.findall(r'\d+(?:\.\d+)?', input_text)
            units = ['mm', 'cm', 'm', 'km', 'ft', 'in', 'kg', 'lb', 'kpa', 'psi', 'degrees']
            unit_count = sum(1 for unit in units if unit in input_lower)
            
            numerical_specificity = min((len(numbers) + unit_count) / 3.0, 1.0)
            specificity_factors.append(numerical_specificity)
            
            # Reference to specific examples or cases
            example_indicators = [
                'for example', 'such as', 'like the', 'similar to', 'case study',
                'project', 'building', 'architect', 'designer'
            ]
            example_count = sum(1 for indicator in example_indicators if indicator in input_lower)
            example_specificity = min(example_count / 2.0, 1.0)
            specificity_factors.append(example_specificity)
            
            # Context-specific references
            if state and hasattr(state, 'messages') and state.messages:
                context_references = ['this', 'that', 'the previous', 'earlier', 'mentioned']
                context_count = sum(1 for ref in context_references if ref in input_lower)
                context_specificity = min(context_count / 3.0, 1.0)
                specificity_factors.append(context_specificity)
            
            return sum(specificity_factors) / len(specificity_factors) if specificity_factors else 0.5
            
        except Exception as e:
            self.telemetry.log_error("_assess_specificity", str(e))
            return 0.5
    
    def _extract_key_topics(self, input_text: str) -> List[str]:
        """Extract key topics from the input text."""
        try:
            # Define topic categories with keywords
            topic_categories = {
                'structural_design': [
                    'structure', 'structural', 'beam', 'column', 'foundation', 'load',
                    'engineering', 'stability', 'strength'
                ],
                'sustainable_design': [
                    'sustainable', 'sustainability', 'green', 'environmental', 'energy',
                    'solar', 'passive', 'renewable', 'efficiency'
                ],
                'building_systems': [
                    'hvac', 'mechanical', 'electrical', 'plumbing', 'lighting', 'ventilation',
                    'heating', 'cooling', 'systems'
                ],
                'materials': [
                    'material', 'materials', 'concrete', 'steel', 'wood', 'timber',
                    'glass', 'brick', 'stone', 'composite'
                ],
                'design_process': [
                    'design', 'planning', 'concept', 'development', 'process', 'methodology',
                    'approach', 'strategy'
                ],
                'building_codes': [
                    'code', 'codes', 'regulation', 'standard', 'compliance', 'requirement',
                    'zoning', 'accessibility', 'safety'
                ],
                'space_planning': [
                    'space', 'planning', 'layout', 'organization', 'circulation', 'zoning',
                    'programming', 'function'
                ]
            }
            
            input_lower = input_text.lower()
            detected_topics = []
            
            for topic, keywords in topic_categories.items():
                keyword_count = sum(1 for keyword in keywords if keyword in input_lower)
                if keyword_count >= 1:  # At least one keyword match
                    detected_topics.append(topic)
            
            # If no specific topics detected, try to extract general architectural concepts
            if not detected_topics:
                general_concepts = self._extract_general_concepts(input_text)
                detected_topics.extend(general_concepts)
            
            return detected_topics[:5]  # Return top 5 topics
            
        except Exception as e:
            self.telemetry.log_error("_extract_key_topics", str(e))
            return ['general_architecture']
    
    def _analyze_content_structure(self, input_text: str) -> Dict[str, Any]:
        """Analyze the structure of the content."""
        try:
            structure_analysis = {
                'word_count': len(input_text.split()),
                'sentence_count': len([s for s in input_text.split('.') if s.strip()]),
                'question_count': input_text.count('?'),
                'exclamation_count': input_text.count('!'),
                'paragraph_count': len([p for p in input_text.split('\n\n') if p.strip()]),
                'has_lists': bool(re.search(r'^\s*[-*•]\s', input_text, re.MULTILINE)),
                'has_numbers': bool(re.search(r'\d+', input_text)),
                'capitalized_words': len(re.findall(r'\b[A-Z][A-Z]+\b', input_text)),
                'average_word_length': 0,
                'structure_complexity': 'simple'
            }
            
            # Calculate average word length
            words = input_text.split()
            if words:
                structure_analysis['average_word_length'] = sum(len(word) for word in words) / len(words)
            
            # Assess structure complexity
            complexity_score = 0
            if structure_analysis['sentence_count'] > 3:
                complexity_score += 1
            if structure_analysis['paragraph_count'] > 1:
                complexity_score += 1
            if structure_analysis['has_lists']:
                complexity_score += 1
            if structure_analysis['average_word_length'] > 6:
                complexity_score += 1
            
            if complexity_score >= 3:
                structure_analysis['structure_complexity'] = 'complex'
            elif complexity_score >= 2:
                structure_analysis['structure_complexity'] = 'moderate'
            
            return structure_analysis
            
        except Exception as e:
            self.telemetry.log_error("_analyze_content_structure", str(e))
            return {'structure_complexity': 'simple', 'word_count': 0}
    
    def _assess_content_quality(self, input_text: str) -> str:
        """Assess the overall quality of the content."""
        try:
            quality_factors = []
            
            # Length appropriateness
            word_count = len(input_text.split())
            if 10 <= word_count <= 200:
                quality_factors.append('appropriate_length')
            elif word_count < 5:
                quality_factors.append('too_short')
            elif word_count > 300:
                quality_factors.append('too_long')
            
            # Grammar and structure indicators
            sentences = [s.strip() for s in input_text.split('.') if s.strip()]
            if sentences:
                # Check for complete sentences
                complete_sentences = sum(1 for s in sentences if len(s.split()) >= 3)
                if complete_sentences / len(sentences) >= 0.7:
                    quality_factors.append('well_structured')
            
            # Vocabulary richness
            words = input_text.split()
            if words:
                unique_words = len(set(word.lower() for word in words))
                vocabulary_richness = unique_words / len(words)
                if vocabulary_richness >= 0.7:
                    quality_factors.append('rich_vocabulary')
                elif vocabulary_richness >= 0.5:
                    quality_factors.append('adequate_vocabulary')
                else:
                    quality_factors.append('limited_vocabulary')
            
            # Technical appropriateness
            technical_terms = self._extract_technical_terms(input_text)
            if len(technical_terms) >= 2:
                quality_factors.append('technically_informed')
            
            # Determine overall quality
            positive_factors = [
                'appropriate_length', 'well_structured', 'rich_vocabulary', 
                'adequate_vocabulary', 'technically_informed'
            ]
            
            positive_count = sum(1 for factor in positive_factors if factor in quality_factors)
            
            if positive_count >= 4:
                return 'high'
            elif positive_count >= 2:
                return 'medium'
            else:
                return 'basic'
                
        except Exception as e:
            self.telemetry.log_error("_assess_content_quality", str(e))
            return 'medium'
    
    def _extract_domain_concepts(self, input_text: str) -> List[str]:
        """Extract domain-specific architectural concepts."""
        try:
            domain_concepts = {
                'design_principles': [
                    'balance', 'proportion', 'scale', 'rhythm', 'emphasis', 'unity',
                    'contrast', 'movement', 'pattern', 'hierarchy'
                ],
                'spatial_concepts': [
                    'space', 'volume', 'void', 'mass', 'circulation', 'flow',
                    'transition', 'threshold', 'boundary', 'enclosure'
                ],
                'environmental_concepts': [
                    'orientation', 'daylight', 'natural ventilation', 'thermal comfort',
                    'microclimate', 'site analysis', 'context', 'landscape'
                ],
                'construction_concepts': [
                    'assembly', 'detail', 'connection', 'joint', 'weathering',
                    'durability', 'maintenance', 'lifecycle', 'performance'
                ]
            }
            
            input_lower = input_text.lower()
            found_concepts = []
            
            for category, concepts in domain_concepts.items():
                for concept in concepts:
                    if concept in input_lower:
                        found_concepts.append(concept)
            
            return found_concepts[:8]  # Return top 8 concepts
            
        except Exception as e:
            self.telemetry.log_error("_extract_domain_concepts", str(e))
            return []
    
    def _assess_information_density(self, input_text: str) -> float:
        """Assess the information density of the text."""
        try:
            words = input_text.split()
            if not words:
                return 0.0
            
            # Count information-rich elements
            technical_terms = len(self._extract_technical_terms(input_text))
            domain_concepts = len(self._extract_domain_concepts(input_text))
            
            # Count numbers and specific references
            import re
            numbers = len(re.findall(r'\d+', input_text))
            proper_nouns = len(re.findall(r'\b[A-Z][a-z]+\b', input_text))
            
            # Calculate density
            total_information_units = technical_terms + domain_concepts + numbers + proper_nouns
            word_count = len(words)
            
            density = total_information_units / word_count if word_count > 0 else 0
            
            # Normalize to 0-1 scale
            return min(density * 3, 1.0)
            
        except Exception as e:
            self.telemetry.log_error("_assess_information_density", str(e))
            return 0.5
    
    def _extract_compound_technical_terms(self, input_text: str) -> List[str]:
        """Extract compound technical terms (multi-word technical phrases)."""
        try:
            compound_terms = [
                'reinforced concrete', 'steel frame', 'curtain wall', 'green roof',
                'passive solar', 'natural ventilation', 'thermal mass', 'building envelope',
                'fire separation', 'seismic design', 'wind load', 'dead load', 'live load',
                'moment frame', 'shear wall', 'foundation system', 'structural system',
                'mechanical system', 'electrical system', 'building code', 'zoning ordinance'
            ]
            
            input_lower = input_text.lower()
            found_compounds = []
            
            for term in compound_terms:
                if term in input_lower:
                    found_compounds.append(term)
            
            return found_compounds
            
        except Exception as e:
            self.telemetry.log_error("_extract_compound_technical_terms", str(e))
            return []
    
    def _extract_general_concepts(self, input_text: str) -> List[str]:
        """Extract general architectural concepts when specific topics aren't found."""
        try:
            general_concepts = [
                'architecture', 'design', 'building', 'construction', 'planning',
                'development', 'project', 'concept', 'idea', 'solution', 'approach'
            ]
            
            input_lower = input_text.lower()
            found_concepts = []
            
            for concept in general_concepts:
                if concept in input_lower:
                    found_concepts.append(concept)
            
            return found_concepts[:3] if found_concepts else ['general_inquiry']
            
        except Exception as e:
            self.telemetry.log_error("_extract_general_concepts", str(e))
            return ['general_inquiry']
    
    def _calculate_analysis_confidence(self, technical_terms: List[str], complexity_score: float,
                                     specificity_score: float, content_quality: str) -> float:
        """Calculate confidence in the content analysis."""
        try:
            confidence_factors = []
            
            # Technical term extraction confidence
            if len(technical_terms) >= 3:
                confidence_factors.append(0.8)
            elif len(technical_terms) >= 1:
                confidence_factors.append(0.6)
            else:
                confidence_factors.append(0.4)
            
            # Complexity assessment confidence
            if complexity_score > 0.7 or complexity_score < 0.3:
                confidence_factors.append(0.8)  # Clear high or low complexity
            else:
                confidence_factors.append(0.6)  # Moderate complexity
            
            # Specificity assessment confidence
            if specificity_score > 0.7 or specificity_score < 0.3:
                confidence_factors.append(0.7)
            else:
                confidence_factors.append(0.5)
            
            # Content quality confidence
            quality_confidence = {'high': 0.8, 'medium': 0.6, 'basic': 0.5}.get(content_quality, 0.5)
            confidence_factors.append(quality_confidence)
            
            return sum(confidence_factors) / len(confidence_factors)
            
        except Exception as e:
            self.telemetry.log_error("_calculate_analysis_confidence", str(e))
            return 0.6
    
    def _get_fallback_content_analysis(self) -> ContentAnalysis:
        """Return fallback content analysis when analysis fails."""
        return ContentAnalysis(
            technical_terms=[],
            emotional_indicators={'positive': 0, 'negative': 0, 'uncertain': 0, 'neutral': 0},
            complexity_score=0.5,
            specificity_score=0.5,
            key_topics=['general_architecture'],
            content_structure={'structure_complexity': 'simple', 'word_count': 0},
            content_quality='medium',
            domain_concepts=[],
            information_density=0.5,
            analysis_confidence=0.4
        ) 