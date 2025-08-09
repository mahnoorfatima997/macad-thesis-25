"""
Knowledge search processing module for web search and knowledge retrieval.
"""
import os
import json
import asyncio
from typing import Dict, Any, List, Optional
from ..config import WEB_SEARCH_CONFIG, SEARCH_ENGINES, KNOWLEDGE_DOMAINS
from ...common import TextProcessor, MetricsCalculator, AgentTelemetry, LLMClient
from state_manager import ArchMentorState


class KnowledgeSearchProcessor:
    """
    Processes knowledge search operations including web search and result processing.
    """
    
    def __init__(self):
        self.telemetry = AgentTelemetry("knowledge_search")
        self.text_processor = TextProcessor()
        self.metrics_calculator = MetricsCalculator()
        self.client = LLMClient()
        # Preferred architecture domains to keep results high-quality and on-topic
        self.preferred_domains = set([
            "dezeen.com", "archdaily.com", "archello.com", "architectural-review.com",
            "architecturaldigest.com", "architectmagazine.com", "architecturalrecord.com",
            "designboom.com", "worldarchitecturenews.com", "bustler.net",
            "archnet.org", "archinect.com", "architecturetoday.co.uk", "landezine.com",
            "divisare.com", "e-architect.com", "metropolismag.com", "domusweb.it",
            "frameweb.com", "world-architects.com", "aia.org", "riba.org", "architecture.com"
        ])
        
        # Initialize search configurations
        self.google_api_key = os.getenv('GOOGLE_API_KEY')
        self.google_cse_id = os.getenv('GOOGLE_CSE_ID')
        self.serp_api_key = os.getenv('SERP_API_KEY')
        
    async def search_web_for_knowledge(self, topic: str, state: ArchMentorState = None) -> List[Dict]:
        """
        Comprehensive web search for architectural knowledge.
        """
        self.telemetry.log_agent_start("search_web_for_knowledge")
        
        try:
            # Determine search modifiers based on context
            modifiers = self.get_search_query_modifiers(topic, state)
            
            # Create optimized search query
            search_query = self._create_web_search_query(topic, modifiers)
            
            # Try multiple search engines
            results = []
            
            # Try Google Custom Search first
            if self.google_api_key and self.google_cse_id:
                google_results = await self._try_google_search(search_query)
                if google_results:
                    results.extend(google_results)
            
            # Try SerpAPI if Google fails or for additional results
            if len(results) < 5 and self.serp_api_key:
                serp_results = await self._try_serp_search(search_query)
                if serp_results:
                    results.extend(serp_results)
            
            # Try enhanced DuckDuckGo as fallback
            if len(results) < 3:
                ddg_results = await self._try_enhanced_duckduckgo(search_query)
                if ddg_results:
                    results.extend(ddg_results)
            
            # If all searches fail, provide fallback knowledge
            if not results:
                results = self._get_architectural_knowledge_fallback(topic)
            
            # Process and enhance results
            processed_results = self._process_search_results(results, topic)
            
            # Validate search quality
            quality_score = self._validate_search_quality(processed_results)
            
            # Track usage for optimization
            self._track_knowledge_usage(topic, len(processed_results))
            
            self.telemetry.log_agent_end("search_web_for_knowledge")
            return processed_results
            
        except Exception as e:
            self.telemetry.log_error("search_web_for_knowledge", str(e))
            return self._get_architectural_knowledge_fallback(topic)
    
    async def _try_google_search(self, query: str) -> List[Dict]:
        """Try Google Custom Search API."""
        try:
            import requests
            
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'key': self.google_api_key,
                'cx': self.google_cse_id,
                'q': query,
                'num': 8,
                'safe': 'active'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                for item in data.get('items', []):
                    results.append({
                        'title': item.get('title', ''),
                        'snippet': item.get('snippet', ''),
                        'url': item.get('link', ''),
                        'source': 'google'
                    })
                
                return results
                
        except Exception as e:
            self.telemetry.log_error("_try_google_search", str(e))
            return []
    
    async def _try_serp_search(self, query: str) -> List[Dict]:
        """Try SerpAPI search."""
        try:
            import requests
            
            url = "https://serpapi.com/search"
            params = {
                'api_key': self.serp_api_key,
                'q': query,
                'engine': 'google',
                'num': 8,
                'safe': 'active'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                for item in data.get('organic_results', []):
                    results.append({
                        'title': item.get('title', ''),
                        'snippet': item.get('snippet', ''),
                        'url': item.get('link', ''),
                        'source': 'serpapi'
                    })
                
                return results
                
        except Exception as e:
            self.telemetry.log_error("_try_serp_search", str(e))
            return []
    
    async def _try_enhanced_duckduckgo(self, query: str) -> List[Dict]:
        """Try enhanced DuckDuckGo search with architectural focus."""
        try:
            # Disable synthetic DDG fallback to avoid low-quality generic snippets
            return []
            
        except Exception as e:
            self.telemetry.log_error("_try_enhanced_duckduckgo", str(e))
            return []
    
    def _get_architectural_knowledge_fallback(self, topic: str) -> List[Dict]:
        """Provide fallback architectural knowledge when searches fail."""
        return self._create_enhanced_fallback_knowledge(topic)
    
    def _create_enhanced_fallback_knowledge(self, topic: str) -> List[Dict]:
        """Create enhanced fallback knowledge based on topic."""
        fallback_knowledge = {
            'sustainable design': [
                {
                    'title': 'Sustainable Architecture Principles',
                    'snippet': 'Key principles include energy efficiency, material selection, water conservation, and site integration.',
                    'url': 'internal://sustainable-design',
                    'source': 'internal'
                }
            ],
            'structural systems': [
                {
                    'title': 'Structural Systems in Architecture',
                    'snippet': 'Common systems include post-and-beam, load-bearing walls, steel frame, and reinforced concrete.',
                    'url': 'internal://structural-systems',
                    'source': 'internal'
                }
            ],
            'building materials': [
                {
                    'title': 'Architectural Materials Guide',
                    'snippet': 'Materials selection affects durability, aesthetics, sustainability, and cost.',
                    'url': 'internal://materials',
                    'source': 'internal'
                }
            ]
        }
        
        # Find best match or create flexible knowledge
        for key, knowledge in fallback_knowledge.items():
            if key.lower() in topic.lower():
                return knowledge
        
        # Generate flexible knowledge for any topic
        return self._generate_flexible_knowledge(topic)
    
    def _generate_flexible_knowledge(self, topic: str) -> List[Dict]:
        """Generate flexible architectural knowledge for any topic."""
        return [
            {
                'title': f'Architectural Considerations for {topic.title()}',
                'snippet': f'In architectural design, {topic} involves careful consideration of form, function, context, and user needs.',
                'url': f'internal://architecture/{topic.replace(" ", "-")}',
                'source': 'internal'
            },
            {
                'title': f'Design Principles: {topic.title()}',
                'snippet': f'Key design principles for {topic} include sustainability, accessibility, aesthetic integration, and technical feasibility.',
                'url': f'internal://principles/{topic.replace(" ", "-")}',
                'source': 'internal'
            }
        ]
    
    def get_search_query_modifiers(self, topic: str, state: ArchMentorState = None) -> List[str]:
        """Get search query modifiers based on context."""
        modifiers = ['architecture', 'design']
        
        if state:
            # Analyze conversation context for modifiers
            context_analysis = self.analyze_conversation_context_for_search(state)
            
            if context_analysis.get('building_type'):
                modifiers.append(context_analysis['building_type'])
            
            if context_analysis.get('focus_area'):
                modifiers.append(context_analysis['focus_area'])
        
        # Add topic-specific modifiers
        if any(word in topic.lower() for word in ['sustainable', 'green', 'eco']):
            modifiers.extend(['sustainability', 'environmental'])
        
        if any(word in topic.lower() for word in ['structure', 'structural', 'engineering']):
            modifiers.extend(['structural', 'engineering'])
        
        if any(word in topic.lower() for word in ['material', 'construction']):
            modifiers.extend(['materials', 'construction'])
        
        return list(set(modifiers))  # Remove duplicates
    
    def analyze_conversation_context_for_search(self, state: ArchMentorState) -> Dict[str, Any]:
        """Analyze conversation context to improve search queries."""
        try:
            user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
            if not user_messages:
                return {}
            
            recent_text = ' '.join(user_messages[-3:]).lower()
            
            context = {}
            
            # Detect building type
            building_types = {
                'residential': ['house', 'home', 'apartment', 'residential'],
                'commercial': ['office', 'retail', 'commercial', 'store'],
                'institutional': ['school', 'hospital', 'library', 'museum'],
                'industrial': ['factory', 'warehouse', 'industrial']
            }
            
            for building_type, keywords in building_types.items():
                if any(keyword in recent_text for keyword in keywords):
                    context['building_type'] = building_type
                    break
            
            # Detect focus area
            focus_areas = {
                'sustainability': ['sustainable', 'green', 'eco', 'energy'],
                'structure': ['structural', 'structure', 'engineering'],
                'materials': ['material', 'construction', 'building'],
                'planning': ['planning', 'layout', 'organization'],
                'aesthetics': ['aesthetic', 'beautiful', 'design', 'appearance']
            }
            
            for focus, keywords in focus_areas.items():
                if any(keyword in recent_text for keyword in keywords):
                    context['focus_area'] = focus
                    break
            
            return context
            
        except Exception as e:
            self.telemetry.log_error("analyze_conversation_context_for_search", str(e))
            return {}
    
    def generate_context_aware_search_query(self, base_topic: str, context: Dict[str, Any]) -> str:
        """Generate context-aware search query."""
        query_parts = [base_topic]
        
        # Add building type context
        if context.get('building_type'):
            query_parts.append(context['building_type'])
        
        # Add focus area context
        if context.get('focus_area'):
            query_parts.append(context['focus_area'])
        
        # Always add architecture context
        query_parts.append('architecture')
        
        return ' '.join(query_parts)
    
    def _create_web_search_query(self, topic: str, modifiers: List[str] = None) -> str:
        """Create optimized web search query."""
        if modifiers is None:
            modifiers = []
        
        # Start with the base topic
        query_parts = [topic]
        
        # Add modifiers
        query_parts.extend(modifiers[:3])  # Limit to avoid over-specification
        
        # Create query
        query = ' '.join(query_parts)
        
        # Ensure query is not too long
        if len(query) > 100:
            query = query[:97] + "..."
        
        return query
    
    def _process_search_results(self, results: List[Dict], topic: str) -> List[Dict]:
        """Process and enhance search results."""
        processed_results = []
        
        def _host(url: str) -> str:
            try:
                from urllib.parse import urlparse
                return urlparse(url).netloc.lower()
            except Exception:
                return ""
        
        for result in results:
            # Filter out placeholder or low-quality domains
            url = result.get('url', '')
            host = _host(url)
            if not url or host.endswith("example.com"):
                continue
            if self.preferred_domains and not any(host.endswith(dom) for dom in self.preferred_domains):
                # Skip non-preferred domains to keep content architectural and high-quality
                continue
            # Score result relevance
            relevance_score = self._score_result_relevance(result, topic)
            
            # Enhance result with additional metadata
            enhanced_result = {
                **result,
                'relevance_score': relevance_score,
                'processed_snippet': self._enhance_snippet(result.get('snippet', '')),
                'key_points': self._extract_key_points_from_result(result),
                'architectural_relevance': self._assess_architectural_relevance(result)
            }
            
            processed_results.append(enhanced_result)
        
        # Sort by relevance score
        processed_results.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        # Return top results
        return processed_results[:8]
    
    def _score_result_relevance(self, result: Dict, topic: str) -> float:
        """Score result relevance to the topic."""
        try:
            title = result.get('title', '').lower()
            snippet = result.get('snippet', '').lower()
            topic_lower = topic.lower()
            
            score = 0.0
            
            # Title relevance (higher weight)
            if topic_lower in title:
                score += 0.5
            
            # Snippet relevance
            if topic_lower in snippet:
                score += 0.3
            
            # Architecture-related terms
            arch_terms = ['architecture', 'design', 'building', 'construction']
            arch_count = sum(1 for term in arch_terms if term in title or term in snippet)
            score += arch_count * 0.1
            
            # Source reliability
            reliable_sources = ['.edu', 'wikipedia', 'archdaily', 'dezeen', 'architectural']
            url = result.get('url', '').lower()
            if any(source in url for source in reliable_sources):
                score += 0.2
            
            return min(score, 1.0)
            
        except Exception as e:
            self.telemetry.log_error("_score_result_relevance", str(e))
            return 0.5
    
    def _enhance_snippet(self, snippet: str) -> str:
        """Enhance snippet for better readability."""
        if not snippet:
            return ""
        
        # Clean up snippet
        enhanced = snippet.strip()
        
        # Ensure it ends properly
        if not enhanced.endswith(('.', '!', '?')):
            enhanced += "..."
        
        return enhanced
    
    def _extract_key_points_from_result(self, result: Dict) -> List[str]:
        """Extract key points from search result."""
        snippet = result.get('snippet', '')
        if not snippet:
            return []
        
        # Simple key point extraction
        sentences = snippet.split('.')
        key_points = []
        
        for sentence in sentences[:3]:  # Limit to 3 points
            sentence = sentence.strip()
            if len(sentence) > 20:  # Filter out very short fragments
                key_points.append(sentence)
        
        return key_points
    
    def _assess_architectural_relevance(self, result: Dict) -> str:
        """Assess how relevant the result is to architecture."""
        title = result.get('title', '').lower()
        snippet = result.get('snippet', '').lower()
        
        arch_keywords = [
            'architecture', 'architectural', 'design', 'building', 'construction',
            'structural', 'planning', 'urban', 'space', 'materials'
        ]
        
        relevance_count = sum(
            1 for keyword in arch_keywords 
            if keyword in title or keyword in snippet
        )
        
        if relevance_count >= 3:
            return "high"
        elif relevance_count >= 1:
            return "medium"
        else:
            return "low"
    
    def _validate_search_quality(self, results: List[Dict]) -> float:
        """Validate the quality of search results."""
        if not results:
            return 0.0
        
        quality_factors = []
        
        # Result count factor
        count_factor = min(len(results) / 5.0, 1.0)
        quality_factors.append(count_factor)
        
        # Average relevance factor
        relevance_scores = [r.get('relevance_score', 0) for r in results]
        avg_relevance = sum(relevance_scores) / len(relevance_scores)
        quality_factors.append(avg_relevance)
        
        # Source diversity factor
        sources = set(r.get('source', 'unknown') for r in results)
        diversity_factor = min(len(sources) / 3.0, 1.0)
        quality_factors.append(diversity_factor)
        
        return sum(quality_factors) / len(quality_factors)
    
    def _track_knowledge_usage(self, topic: str, results_count: int) -> None:
        """Track knowledge usage for optimization."""
        try:
            # Simple usage tracking (could be enhanced with proper analytics)
            usage_data = {
                'topic': topic,
                'results_count': results_count,
                'timestamp': self.telemetry.get_timestamp()
            }
            
            # Log for analytics
            self.telemetry.log_metric("knowledge_usage", usage_data)
            
        except Exception as e:
            self.telemetry.log_error("_track_knowledge_usage", str(e))
    
    def is_building_request(self, text: str) -> bool:
        """Check if the request is about buildings."""
        building_indicators = [
            'building', 'structure', 'construction', 'architecture', 'design',
            'house', 'office', 'residential', 'commercial', 'institutional'
        ]
        
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in building_indicators)
    
    def is_landscape_request(self, text: str) -> bool:
        """Check if the request is about landscape architecture."""
        landscape_indicators = [
            'landscape', 'garden', 'outdoor', 'site', 'park', 'plaza',
            'courtyard', 'green space', 'urban planning', 'site design'
        ]
        
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in landscape_indicators) 