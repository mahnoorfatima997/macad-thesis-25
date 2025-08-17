"""
Knowledge search processing module for web search and knowledge retrieval.
"""
import os
import json
import asyncio
import re
import unicodedata
import logging
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse
from ..config import WEB_SEARCH_CONFIG, SEARCH_ENGINES, KNOWLEDGE_DOMAINS
from ...common import TextProcessor, MetricsCalculator, AgentTelemetry, LLMClient
from state_manager import ArchMentorState


# ENHANCED: Preferred architectural domains for Tavily search filtering
ARCHITECTURAL_SOURCES = [
    "site:archdaily.com",
    "site:dezeen.com",
    "site:architecturalrecord.com",
    "site:architecturaldigest.com",
    "site:archpaper.com",
    "site:e-architect.com",
    "site:metropolismag.com",
    "site:domusweb.it",
    "site:frameweb.com",
    "site:world-architects.com"
]

def get_preferred_architecture_domains() -> List[str]:
    """Return a whitelist of preferred architecture domains from ARCHITECTURAL_SOURCES."""
    cleaned: List[str] = []
    for source in ARCHITECTURAL_SOURCES:
        domain = source.replace("site:", "").strip()
        if domain and domain not in cleaned:
            cleaned.append(domain)
    return cleaned


def generate_alternate_search_query(query: str) -> str:
    """Create an alternate query to fetch case-study oriented results if the first query is too broad."""
    q = (query or '').strip()
    q_lower = q.lower()
    if any(k in q_lower for k in [
        'case study', 'case studies', 'example', 'examples', 'project', 'precedent'
    ]):
        return q
    alt = f"{q} architectural case studies project examples"
    alt = re.sub(r"\s+", " ", alt).strip()
    return alt[:200]


def generate_context_aware_search_query(topic: str, context: Dict[str, Any]) -> str:
    """Generate a robust, sanitized search query from topic + context."""

    def _norm(s: str) -> str:
        return unicodedata.normalize('NFKD', s or '').encode('ascii', 'ignore').decode('ascii')

    raw = _norm((topic or '').strip())

    # Remove conversational fillers/questions
    fillers = [
        r"\bi don'?t know\b", r"\bcan you\b", r"\bcould you\b", r"\bplease\b",
        r"\bgive me\b", r"\bsome of them\b", r"\bshow me\b", r"\bprovide\b",
        r"\bwhat is\b", r"\bwhat are\b", r"\bhow (do|to|can)\b", r"\bhelp\b"
    ]
    lowered = raw.lower()
    for f in fillers:
        lowered = re.sub(f, " ", lowered)

    # Keep only words, spaces and dashes; collapse spaces
    cleaned = re.sub(r"[^\w\s-]", " ", lowered)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    parts = []
    if cleaned:
        parts.append(cleaned)

    bt = context.get('building_type')
    if bt and bt != 'general':
        parts.append(_norm(bt).replace('_', ' '))

    elems = context.get('specific_elements') or []
    if elems:
        parts.extend(_norm(e) for e in elems[:2])

    parts.append('architecture')

    # Add intent-based boosters for better results
    intent_boosters = []
    topic_lower = (topic or '').lower()
    if any(k in topic_lower for k in ['example', 'examples', 'project', 'case study', 'case studies', 'precedent', 'built project']):
        intent_boosters.extend(['case study', 'project example', 'architectural precedent'])

    if intent_boosters:
        parts.extend(intent_boosters)

    query = " ".join(p for p in parts if p).strip()
    if len(query) > 150:
        query = query[:150]
    return query


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
        
        # ENHANCED: Initialize Tavily API configuration (sole web search provider)
        try:
            import sys
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'utils'))
            from secrets_manager import get_tavily_api_key
            self.tavily_api_key = get_tavily_api_key()
        except ImportError:
            # Fallback if secrets_manager is not available
            self.tavily_api_key = os.getenv('TAVILY_API_KEY')

        # ENHANCED: Simple in-memory cache for web search results (reduces API calls)
        self._web_cache: Dict[str, List[Dict]] = {}
        self._web_cache_max_entries: int = 64
        
    async def search_web_for_knowledge(self, topic: str, state: ArchMentorState = None) -> List[Dict]:
        """Web search using only Tavily, with contextual queries, caching, and safe fallback."""

        logger = logging.getLogger(__name__)
        try:
            # Analyze conversation context for better search queries
            context = {}
            if state:
                context = self.analyze_conversation_context_for_search(state)
                logger.debug("Web search context: %s", context)

            # Generate enhanced context-aware search query
            search_query = self.generate_enhanced_search_query(topic, context)
            logger.info("Enhanced Tavily search query: %s", search_query)

            # Cache key incorporates query and key context fields
            cache_key = f"{search_query}::bt={context.get('building_type','')}"
            if cache_key in self._web_cache:
                logger.debug("Using cached web results for query")
                return self._web_cache[cache_key]

            # Use Tavily as the sole web search provider
            results: List[Dict] = []
            tavily_results = await self._try_tavily_search(search_query, context)
            if tavily_results:
                results.extend(tavily_results)
                logger.info("Tavily search returned %d results", len(tavily_results))

            # If no results, try an alternate, case-study-focused query with Tavily
            if not results:
                alt_query = generate_alternate_search_query(search_query)
                if alt_query != search_query:
                    logger.debug("Retrying tavily with alternate query: %s", alt_query)
                    tavily_alt_results = await self._try_tavily_search(alt_query, context)
                    if tavily_alt_results:
                        results.extend(tavily_alt_results)
                        logger.info("Alternate Tavily search returned %d results", len(tavily_alt_results))

            # Fallback to architectural knowledge base
            if not results:
                logger.warning("No Tavily results found, using architectural knowledge fallback")
                results = self._get_architectural_knowledge_fallback(topic)

            # Store in cache (simple bound)
            if len(self._web_cache) >= self._web_cache_max_entries:
                # remove an arbitrary item (FIFO-ish)
                oldest_key = next(iter(self._web_cache))
                del self._web_cache[oldest_key]

            self._web_cache[cache_key] = results

            return results

        except Exception as e:
            logger.error("Tavily web search failed: %s", e)
            return self._get_architectural_knowledge_fallback(topic)
    
    # REMOVED: Old Google search method - replaced with Tavily
    
    # REMOVED: Old SerpAPI search method - replaced with Tavily

    async def _try_tavily_search(self, query: str, context: Dict[str, Any] = None) -> List[Dict]:
        """Enhanced Tavily API search with better error handling and fallback strategies."""
        logger = logging.getLogger(__name__)

        # Check cache first
        cache_key = f"tavily:{query}"
        if cache_key in self._web_cache:
            logger.debug(f"Using cached Tavily results for: {query}")
            return self._web_cache[cache_key]

        try:
            import requests

            if not self.tavily_api_key:
                logger.warning("TAVILY_API_KEY missing; web search disabled")
                return []

            include_domains = get_preferred_architecture_domains()

            # Enhanced payload with better search parameters
            payload = {
                'api_key': self.tavily_api_key,
                'query': query,
                'search_depth': 'advanced',
                'max_results': 10,  # Increased for better results
                'include_answer': False,
                'include_raw_content': False,
                'include_images': False,
                'format': 'json'
            }

            # Always restrict to domain whitelist to avoid irrelevant sources
            if include_domains:
                payload['include_domains'] = include_domains

            url = 'https://api.tavily.com/search'

            # Enhanced request with better timeout and headers
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'ArchMentor/1.0'
            }

            response = requests.post(url, json=payload, headers=headers, timeout=30)

            if response.status_code == 200:
                data = response.json()
                items: List[Dict] = []
                allowed = set(include_domains) if include_domains else set()

                results = data.get('results', [])
                logger.info(f"Tavily API returned {len(results)} raw results")

                for r in results[:12]:  # Process up to 12 results
                    title = r.get('title', '').strip()
                    snippet = (r.get('content') or r.get('snippet', '')).strip()
                    url_result = r.get('url', '').strip()

                    # Skip empty results
                    if not title or not snippet or not url_result:
                        continue

                    # Enhanced domain filtering
                    try:
                        from urllib.parse import urlparse
                        host = urlparse(url_result).netloc.lower()
                        if allowed and not any(host.endswith(dom.lower()) for dom in allowed):
                            logger.debug(f"Filtered out result from {host}")
                            continue
                    except Exception as e:
                        logger.debug(f"URL parsing failed for {url_result}: {e}")
                        continue

                    # Enhanced result structure
                    items.append({
                        'content': snippet,
                        'metadata': {
                            'title': title,
                            'url': url_result,
                            'source': 'tavily',
                            'type': 'web_result',
                            'domain': host,
                            'relevance_score': r.get('score', 0.5)
                        },
                        'discovery_method': 'web'
                    })

                # Cache results with better management
                if len(self._web_cache) >= self._web_cache_max_entries:
                    # Remove oldest entry (FIFO)
                    oldest_key = next(iter(self._web_cache))
                    del self._web_cache[oldest_key]

                self._web_cache[cache_key] = items

                logger.info(f"Tavily search returned {len(items)} filtered results for: {query}")
                return items

            elif response.status_code == 401:
                logger.error("Tavily API authentication failed - check TAVILY_API_KEY")
            elif response.status_code == 429:
                logger.warning("Tavily API rate limit exceeded")
            else:
                logger.error(f"Tavily API error: {response.status_code} - {response.text}")

        except requests.exceptions.Timeout:
            logger.error("Tavily search timed out")
        except requests.exceptions.ConnectionError:
            logger.error("Tavily search connection failed")
        except Exception as e:
            logger.error(f"Tavily search failed: {e}")

        return []

    # REMOVED: Old DuckDuckGo search method - replaced with Tavily

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

            # UPDATED: Use centralized building type detection to avoid duplications
            # Get building type from state instead of detecting locally
            if hasattr(state, 'conversation_context') and state.conversation_context.detected_building_type:
                context['building_type'] = state.conversation_context.detected_building_type
            elif hasattr(state, 'building_type') and state.building_type and state.building_type != "unknown":
                context['building_type'] = state.building_type
            else:
                # Only perform local detection as fallback if no centralized detection exists
                # IMPORTANT: Only extract from design brief and first user message, NOT all messages
                detection_text = ""
                if hasattr(state, 'current_design_brief') and state.current_design_brief:
                    detection_text = state.current_design_brief.lower()
                elif user_messages:
                    detection_text = user_messages[0].lower()  # ONLY first message

                if detection_text:
                    building_types = {
                        'residential': ['house', 'home', 'apartment', 'residential'],
                        'commercial': ['office', 'retail', 'commercial', 'store'],
                        'institutional': ['school', 'hospital', 'library', 'museum'],
                        'community': ['community center', 'civic center']
                    }

                    for building_type, keywords in building_types.items():
                        if any(keyword in detection_text for keyword in keywords):
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

            # ENHANCED: Extract specific architectural elements mentioned
            specific_elements = []
            architectural_elements = [
                'atrium', 'courtyard', 'facade', 'entrance', 'lobby', 'circulation',
                'lighting', 'ventilation', 'roof', 'foundation', 'stairs', 'elevator',
                'balcony', 'terrace', 'window', 'door', 'wall', 'column', 'beam'
            ]

            for element in architectural_elements:
                if element in recent_text:
                    specific_elements.append(element)

            if specific_elements:
                context['specific_elements'] = specific_elements[:3]  # Limit to top 3

            return context
            
        except Exception as e:
            self.telemetry.log_error("analyze_conversation_context_for_search", str(e))
            return {}
    
    def generate_enhanced_search_query(self, base_topic: str, context: Dict[str, Any]) -> str:
        """Generate enhanced context-aware search query with conversation continuity."""
        query_parts = [base_topic]

        # Add building type context from conversation continuity
        building_type = context.get('building_type')
        if not building_type and hasattr(context, 'detected_building_type'):
            building_type = context.detected_building_type

        if building_type and building_type != "unknown":
            query_parts.append(building_type)

        # Add focus area context
        if context.get('focus_area'):
            query_parts.append(context['focus_area'])

        # Add design phase context if available
        if context.get('design_phase') and context['design_phase'] != "ideation":
            query_parts.append(context['design_phase'])

        # Always add architecture context for relevance
        query_parts.append('architecture')

        # Add specific modifiers based on context
        if context.get('is_example_request'):
            query_parts.append('examples')
        if context.get('is_case_study_request'):
            query_parts.append('case studies')

        query = ' '.join(query_parts)

        # Clean and optimize the query
        query = re.sub(r'\s+', ' ', query).strip()
        return query[:150]  # Limit length for API efficiency
    
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