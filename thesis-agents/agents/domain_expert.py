# agents/domain_expert.py - COMPLETELY REWRITTEN for creativity and flexibility

from typing import Dict, Any, List
import os
from openai import OpenAI
from dotenv import load_dotenv
import sys
import re

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import development configuration for cost-efficient testing
try:
    from config.development_config import dev_config, should_skip_expensive_call, get_dev_token_limit
except ImportError:
    # Fallback if config not available
    class MockDevConfig:
        def get_model(self, use_case="cheap"): return "gpt-4o"
        def get_token_limit(self, component): return 200
        def is_feature_enabled(self, feature): return True
        def get_mock_response(self, component): return {}
    dev_config = MockDevConfig()
    def should_skip_expensive_call(feature): return False
    def get_dev_token_limit(component): return 200

from state_manager import ArchMentorState
from knowledge_base.knowledge_manager import KnowledgeManager
from utils.agent_response import AgentResponse, ResponseType, CognitiveFlag, ResponseBuilder, EnhancementMetrics

# Enhanced architectural sources for better search results
ARCHITECTURAL_SOURCES = [
    "site:dezeen.com", "site:archdaily.com", "site:archello.com", 
    "site:architectural-review.com", "site:architecturaldigest.com", 
    "site:architectmagazine.com", "site:architecturalrecord.com",
    "site:architect.org", "site:aia.org", "site:architecturalleague.org",
    "site:architecturalfoundation.org", "site:architecturalassociation.org.uk",
    "site:architecturalrecord.com", "site:architecturaldigest.com"
]

# Comprehensive architectural keyword configuration for flexible detection
ARCHITECTURAL_KEYWORDS = {
    "building_types": {
        "residential": [
            "house", "home", "apartment", "condo", "townhouse", "villa", "mansion", "cottage", 
            "bungalow", "duplex", "triplex", "penthouse", "loft", "studio", "dormitory", "residence"
        ],
        "commercial": [
            "office", "retail", "shop", "store", "mall", "market", "restaurant", "cafe", "hotel", 
            "motel", "inn", "resort", "spa", "gym", "fitness", "cinema", "theater", "auditorium", 
            "conference", "exhibition", "gallery", "showroom", "warehouse", "factory", "industrial"
        ],
        "institutional": [
            "school", "university", "college", "academy", "institute", "hospital", "clinic", 
            "medical", "library", "museum", "archive", "courthouse", "city hall", "government", 
            "police", "fire station", "post office", "bank", "church", "temple", "mosque", "synagogue"
        ],
        "community": [
            "community center", "community hall", "recreation center", "youth center", "senior center",
            "cultural center", "arts center", "performance center", "multipurpose", "civic center",
            "town hall", "meeting hall", "assembly hall", "convention center", "exhibition center"
        ],
        "transportation": [
            "airport", "train station", "bus station", "metro", "subway", "terminal", "depot",
            "garage", "parking", "bridge", "tunnel", "port", "marina"
        ],
        "mixed_use": [
            "mixed use", "mixed-use", "live work", "live-work", "commercial residential",
            "retail residential", "office residential", "integrated", "complex", "development"
        ]
    },
    "building_elements": [
        "building", "structure", "facility", "center", "complex", "tower", "block", "wing",
        "annex", "extension", "addition", "renovation", "conversion", "adaptive reuse",
        "repurposing", "retrofitting", "rehabilitation", "restoration", "preservation"
    ],
    "landscape_types": [
        "landscape", "park", "garden", "outdoor", "public space", "plaza", "square", "courtyard",
        "terrace", "rooftop garden", "green roof", "urban park", "botanical garden", "arboretum",
        "playground", "sports field", "athletic", "recreation area", "trail", "pathway", "walkway",
        "promenade", "esplanade", "boulevard", "street", "alley", "pedestrian", "bike path"
    ],
    "urban_elements": [
        "urban", "city", "downtown", "neighborhood", "district", "zone", "area", "precinct",
        "quarter", "block", "street", "avenue", "road", "highway", "infrastructure", "utilities"
    ]
}

def is_building_request(text: str) -> bool:
    """
    Flexible detection of building-related requests using comprehensive keyword matching.
    Returns True if the text indicates a request for building examples/information.
    """
    text_lower = text.lower()
    
    # Check for building types
    for category, keywords in ARCHITECTURAL_KEYWORDS["building_types"].items():
        if any(keyword in text_lower for keyword in keywords):
            return True
    
    # Check for building elements
    if any(keyword in text_lower for keyword in ARCHITECTURAL_KEYWORDS["building_elements"]):
        return True
    
    return False

def is_landscape_request(text: str) -> bool:
    """
    Flexible detection of landscape-related requests using comprehensive keyword matching.
    Returns True if the text indicates a request for landscape examples/information.
    """
    text_lower = text.lower()
    
    # Check for landscape types
    if any(keyword in text_lower for keyword in ARCHITECTURAL_KEYWORDS["landscape_types"]):
        return True
    
    return False

def get_search_query_modifiers(text: str) -> Dict[str, str]:
    """
    Returns appropriate search query modifiers based on the type of request detected.
    """
    text_lower = text.lower()
    
    if is_building_request(text):
        # Exclude landscape and urban projects when building is requested
        return {
            "include": "building architecture",
            "exclude": "-landscape -park -urban -garden -outdoor -public space -plaza"
        }
    elif is_landscape_request(text):
        # Focus on landscape and urban projects
        return {
            "include": "landscape architecture",
            "exclude": ""
        }
    else:
        # Default to general architecture
        return {
            "include": "architecture",
            "exclude": ""
        }

def analyze_conversation_context_for_search(state: ArchMentorState) -> Dict[str, Any]:
    """
    Analyze conversation context to extract search-relevant information.
    Returns context that can be used to generate more targeted search queries.
    """
    context = {
        "building_type": "general",
        "project_scope": "unknown",
        "specific_elements": [],
        "user_needs": [],
        "technical_requirements": [],
        "design_phase": "ideation",
        "conversation_themes": []
    }
    
    # Extract building type from conversation
    user_messages = [msg.get('content', '') for msg in state.messages if msg.get('role') == 'user']
    assistant_messages = [msg.get('content', '') for msg in state.messages if msg.get('role') == 'assistant']
    
    # Analyze user messages for building type
    for message in user_messages:
        message_lower = message.lower()
        
        # Detect building types
        for category, keywords in ARCHITECTURAL_KEYWORDS["building_types"].items():
            if any(keyword in message_lower for keyword in keywords):
                context["building_type"] = category
                break
        
        # Detect specific elements
        for element in ARCHITECTURAL_KEYWORDS["building_elements"]:
            if element in message_lower:
                context["specific_elements"].append(element)
        
        # Detect user needs (accessibility, sustainability, etc.)
        if any(word in message_lower for word in ["accessible", "disability", "wheelchair", "elderly", "senior"]):
            context["user_needs"].append("accessibility")
        if any(word in message_lower for word in ["sustainable", "green", "eco", "energy", "solar"]):
            context["user_needs"].append("sustainability")
        if any(word in message_lower for word in ["budget", "cost", "affordable", "economic"]):
            context["user_needs"].append("budget_constraints")
        if any(word in message_lower for word in ["adaptive reuse", "conversion", "renovation", "repurpose"]):
            context["user_needs"].append("adaptive_reuse")
    
    # Extract design phase from state
    if hasattr(state, 'design_phase') and state.design_phase:
        context["design_phase"] = state.design_phase.value if hasattr(state.design_phase, 'value') else str(state.design_phase)
    
    return context

def generate_context_aware_search_query(topic: str, context: Dict[str, Any]) -> str:
    """Generate a robust, sanitized search query from topic + context."""
    import re
    import unicodedata

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

    query = " ".join(p for p in parts if p).strip()
    if len(query) > 150:
        query = query[:150]
    return query

class DomainExpertAgent:
    def __init__(self, domain="architecture"):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.domain = domain
        self.name = "domain_expert"
        self.knowledge_manager = KnowledgeManager(domain)
        
        print(f"📚 {self.name} initialized with knowledge base for {domain}")

    # Enhanced web search with context awareness
    async def search_web_for_knowledge(self, topic: str, state: ArchMentorState = None) -> List[Dict]:
        """Enhanced web search with better search methods and fallback strategies"""
        
        try:
            import requests
            from urllib.parse import quote
            import re
            import json
            
            # Analyze conversation context for better search queries
            context = {}
            if state:
                context = analyze_conversation_context_for_search(state)
                print(f"🔍 Context analysis: {context}")
            
            # Generate context-aware search query
            search_query = generate_context_aware_search_query(topic, context)
            print(f"🌐 Enhanced web search: {search_query}")
            
            # Try multiple search strategies
            results = []
            
            # Strategy 1: Try Google Custom Search API (if available)
            google_results = await self._try_google_search(search_query)
            if google_results:
                results.extend(google_results)
                print(f"✅ Google search found {len(google_results)} results")
            
            # Strategy 2: Try SerpAPI (if available)
            if not results:
                serp_results = await self._try_serp_search(search_query)
                if serp_results:
                    results.extend(serp_results)
                    print(f"✅ SerpAPI search found {len(serp_results)} results")
            
            # Strategy 3: Enhanced DuckDuckGo with better parsing
            if not results:
                ddg_results = await self._try_enhanced_duckduckgo(search_query)
                if ddg_results:
                    results.extend(ddg_results)
                    print(f"✅ Enhanced DuckDuckGo found {len(ddg_results)} results")
            
            # Strategy 4: Fallback to architectural knowledge base
            if not results:
                print("⚠️ No web results found, using architectural knowledge base")
                results = await self._get_architectural_knowledge_fallback(topic, context)
            
            return results
            
        except Exception as e:
            print(f"❌ Web search failed: {e}")
            return await self._get_architectural_knowledge_fallback(topic, context)
    
    async def _try_google_search(self, query: str) -> List[Dict]:
        """Try Google Custom Search API"""
        try:
            api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
            cx = os.getenv("GOOGLE_SEARCH_CX")
            
            if not api_key or not cx:
                return []
            
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'key': api_key,
                'cx': cx,
                'q': query,
                'num': 5
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
                        'source': 'google',
                        'is_web_result': True
                    })
                
                return results
        except Exception as e:
            print(f"Google search failed: {e}")
        
        return []
    
    async def _try_serp_search(self, query: str) -> List[Dict]:
        """Try SerpAPI for web search"""
        try:
            api_key = os.getenv("SERPAPI_KEY")
            if not api_key:
                return []
            
            url = "https://serpapi.com/search"
            params = {
                'api_key': api_key,
                'q': query,
                'engine': 'google',
                'num': 5
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                results = []
                
                for result in data.get('organic_results', []):
                    results.append({
                        'title': result.get('title', ''),
                        'snippet': result.get('snippet', ''),
                        'url': result.get('link', ''),
                        'source': 'serpapi',
                        'is_web_result': True
                    })
                
                return results
        except Exception as e:
            print(f"SerpAPI search failed: {e}")
        
        return []
    
    async def _try_enhanced_duckduckgo(self, query: str) -> List[Dict]:
        """Enhanced DuckDuckGo search with better parsing"""
        try:
            import requests
            from urllib.parse import quote
            
            encoded_query = quote(query)
            search_url = f"https://duckduckgo.com/html/?q={encoded_query}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
            
            response = requests.get(search_url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                results = []
                
                # Multiple patterns to catch different DuckDuckGo layouts
                patterns = [
                    r'<a[^>]*class="result__a"[^>]*>([^<]+)</a>',
                    r'<a[^>]*class="result__title"[^>]*>([^<]+)</a>',
                    r'<a[^>]*class="[^"]*result[^"]*"[^>]*>([^<]+)</a>',
                    r'<h2[^>]*><a[^>]*>([^<]+)</a></h2>',
                    r'<a[^>]*href="[^"]*"[^>]*>([^<]+)</a>'
                ]
                
                snippet_patterns = [
                    r'<a[^>]*class="result__snippet"[^>]*>([^<]+)</a>',
                    r'<span[^>]*class="result__snippet"[^>]*>([^<]+)</span>',
                    r'<div[^>]*class="[^"]*snippet[^"]*"[^>]*>([^<]+)</div>'
                ]
                
                url_patterns = [
                    r'<a[^>]*class="result__a"[^>]*href="([^"]+)"',
                    r'<a[^>]*class="result__title"[^>]*href="([^"]+)"',
                    r'<a[^>]*href="([^"]+)"[^>]*class="[^"]*result[^"]*"'
                ]
                
                titles = []
                snippets = []
                urls = []
                
                # Try all patterns
                for pattern in patterns:
                    titles.extend(re.findall(pattern, response.text))
                    if titles:
                        break
                
                for pattern in snippet_patterns:
                    snippets.extend(re.findall(pattern, response.text))
                    if snippets:
                        break
                
                for pattern in url_patterns:
                    urls.extend(re.findall(pattern, response.text))
                    if urls:
                        break
                
                # Clean and filter results
                for i in range(min(5, len(titles))):
                    try:
                        title = titles[i] if i < len(titles) else "Architectural Resource"
                        snippet = snippets[i] if i < len(snippets) else ""
                        url = urls[i] if i < len(urls) else ""
                        
                        # Clean HTML entities
                        title = re.sub(r'&[a-zA-Z]+;', '', title).strip()
                        snippet = re.sub(r'&[a-zA-Z]+;', '', snippet).strip()
                        
                        # Filter out non-architectural results
                        if any(arch_term in title.lower() or arch_term in snippet.lower() 
                               for arch_term in ['architecture', 'design', 'building', 'construction', 'project']):
                            results.append({
                                'title': title,
                                'snippet': snippet,
                                'url': url,
                                'source': 'duckduckgo',
                                'is_web_result': True
                            })
                    
                    except Exception as e:
                        print(f"Error processing result {i}: {e}")
                        continue
                
                return results
                
        except Exception as e:
            print(f"Enhanced DuckDuckGo search failed: {e}")
        
        return []
    
    async def _get_architectural_knowledge_fallback(self, topic: str, context: Dict) -> List[Dict]:
        """Fallback to architectural knowledge base"""
        try:
            # Generate AI-based architectural examples
            building_type = context.get('building_type', 'general')
            
            # Create structured architectural knowledge
            knowledge_base = {
                'adaptive_reuse': [
                    {
                        'title': 'Tate Modern, London',
                        'snippet': 'Former power station transformed into world-class art museum, demonstrating successful adaptive reuse of industrial heritage.',
                        'url': 'https://www.tate.org.uk/visit/tate-modern',
                        'source': 'architectural_knowledge',
                        'is_web_result': False
                    },
                    {
                        'title': 'The High Line, New York',
                        'snippet': 'Abandoned elevated railway converted into innovative public park, showing creative adaptive reuse of infrastructure.',
                        'url': 'https://www.thehighline.org/',
                        'source': 'architectural_knowledge',
                        'is_web_result': False
                    }
                ],
                'community_center': [
                    {
                        'title': 'Kulturhuset Stadsteatern, Stockholm',
                        'snippet': 'Cultural center utilizing extensive glazing for natural light, creating flexible community spaces.',
                        'url': 'https://www.stadsteatern.stockholm.se/',
                        'source': 'architectural_knowledge',
                        'is_web_result': False
                    },
                    {
                        'title': 'The Factory, Manchester',
                        'snippet': 'Former industrial building transformed into vibrant community arts and performance space.',
                        'url': 'https://www.factorymanchester.com/',
                        'source': 'architectural_knowledge',
                        'is_web_result': False
                    }
                ],
                'sports_facility': [
                    {
                        'title': 'Olympic Park, London',
                        'snippet': 'Former industrial site transformed into world-class sports facilities and public park.',
                        'url': 'https://www.queenelizabetholympicpark.co.uk/',
                        'source': 'architectural_knowledge',
                        'is_web_result': False
                    }
                ]
            }
            
            # Match topic to knowledge base
            if 'adaptive' in topic.lower() or 'reuse' in topic.lower():
                return knowledge_base.get('adaptive_reuse', [])
            elif 'community' in topic.lower() or 'center' in topic.lower():
                return knowledge_base.get('community_center', [])
            elif 'sport' in topic.lower():
                return knowledge_base.get('sports_facility', [])
            else:
                # Return general architectural examples
                all_examples = []
                for category in knowledge_base.values():
                    all_examples.extend(category)
                return all_examples[:3]
                
        except Exception as e:
            print(f"Architectural knowledge fallback failed: {e}")
            return []

    def _create_enhanced_fallback_knowledge(self, topic: str) -> List[Dict]:
        """Enhanced fallback knowledge with better example-focused content"""
        
        # Enhanced fallback content that addresses example requests better
        if any(word in topic.lower() for word in ["example", "project", "precedent"]):
            # For example requests, provide project-focused content
            fallback_content = f"While I don't have specific project examples readily available for {topic}, I can guide you toward key principles that successful projects typically demonstrate. Consider looking at award-winning projects in architectural databases like ArchDaily, Dezeen, or the AIA Awards that showcase {topic}. These resources often feature detailed case studies with photos, plans, and architect insights that can provide the concrete examples you're seeking."
        else:
            # For general topics, provide enhanced principle-based content
            fallback_knowledge = {
                "lighting": "Architectural lighting design involves both natural and artificial light sources. Natural lighting strategies include strategic window placement, skylights, light wells, and clerestory windows to maximize daylight penetration while controlling glare. Artificial lighting should layer ambient, task, and accent lighting. Key principles include avoiding harsh contrasts, creating visual comfort, supporting circadian rhythms through dynamic lighting, and considering both functional and atmospheric needs.",
                
                "acoustics": "Acoustic design in architecture focuses on controlling sound transmission and creating appropriate sound environments. Key strategies include using sound-absorbing materials like acoustic panels, soft furnishings, and textured surfaces; designing proper room shapes to avoid sound focusing and echo; creating acoustic separation between noisy and quiet spaces; and considering both noise reduction and speech intelligibility for the intended use.",
                
                "accessibility": "Universal design principles ensure spaces are usable by people of all abilities. Key requirements include barrier-free access with ramps (1:12 slope max), elevators, adequate door widths (minimum 32 inches clear), accessible restrooms with proper clearances, appropriate signage with tactile elements, and considering sensory impairments through visual, auditory, and tactile cues throughout the design.",
                
                "materials": "Architectural material selection involves considering durability, aesthetics, environmental impact, maintenance, and performance. Sustainable approaches include reclaimed wood, recycled steel, low-VOC finishes, locally sourced materials, and rapidly renewable resources. Consider how materials age, their thermal properties, embodied energy, lifecycle costs, and how they contribute to the overall design narrative and user experience.",
                
                "circulation": "Circulation design focuses on how people move through spaces efficiently and intuitively. Principles include creating clear sight lines for wayfinding, providing adequate corridor widths (minimum 44 inches for accessibility), designing logical flow patterns that match user behavior, ensuring emergency egress compliance, and considering vertical circulation through strategically placed stairs and elevators that become architectural features.",
                
                "sustainability": "Sustainable architecture incorporates passive design strategies, renewable energy systems, water conservation, and sustainable materials. Key approaches include building orientation for solar gain, high-performance insulation and windows, efficient HVAC systems, green roofs and walls, rainwater harvesting, natural ventilation, and designing for building longevity, adaptability, and eventual deconstruction."
            }
            
            # Match topic to specific knowledge
            topic_lower = topic.lower()
            fallback_content = None
            
            for key, content in fallback_knowledge.items():
                if key in topic_lower:
                    fallback_content = content
                    break
            
            if not fallback_content:
                fallback_content = f"Architectural design for {topic} involves considering user needs, functional requirements, environmental factors, and aesthetic goals. Key principles include human scale, accessibility, sustainability, and contextual sensitivity. Design solutions should balance form and function while creating meaningful spaces that serve their intended purpose effectively and contribute positively to their context."
        
        return [{
            "content": fallback_content,
            "metadata": {
                "title": f"Enhanced Architectural Guidance: {topic.title()}",
                "source": "Enhanced Architectural Knowledge Base",
                "type": "enhanced_fallback_knowledge",
                "topic": topic
            },
            "similarity": 0.75
        }]
    
    def _generate_flexible_knowledge(self, topic: str) -> List[Dict]:
        """Generate flexible, AI-powered knowledge for ANY architectural topic"""
        
        try:
            from openai import OpenAI
            import os
            
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            
            # AI prompt to generate contextually relevant architectural knowledge
            prompt = f"""
            Generate comprehensive architectural knowledge about: {topic}
            
            REQUIREMENTS:
            1. Provide general principles and approaches for this topic in architecture
            2. Include practical considerations and design strategies
            3. Focus on how this applies to various building types
            4. Keep it educational and informative
            5. Avoid specific building names or hardcoded examples
            6. Make it applicable to different architectural contexts
            
            Format: Provide 2-3 key principles or approaches with brief explanations.
            Keep under 150 words. Focus on general architectural knowledge.
            """
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.6
            )
            
            ai_generated_content = response.choices[0].message.content.strip()
            
            return [{
                "content": ai_generated_content,
                "metadata": {
                    "title": f"Architectural Principles: {topic.title()}",
                    "source": "AI-Generated Architectural Knowledge",
                    "type": "flexible_knowledge"
                },
                "similarity": 0.7
            }]
            
        except Exception as e:
            print(f"⚠️ AI knowledge generation failed: {e}")
            # Final fallback - very general guidance
            general_content = f"Architectural design for {topic} involves considering user needs, functional requirements, environmental factors, and aesthetic goals. Key principles include human scale, accessibility, sustainability, and contextual sensitivity. Design solutions should balance form and function while creating meaningful spaces that serve their intended purpose effectively."
            
            return [{
                "content": general_content,
                "metadata": {
                    "title": f"Architectural Principles: {topic.title()}",
                    "source": "General Architectural Knowledge",
                    "type": "fallback_knowledge"
                },
                "similarity": 0.7
            }]
    
    async def _generate_flexible_example_prompt(self, user_topic: str, building_type: str, project_context: str, combined_knowledge: str, user_request: str) -> str:
        """Generate AI-powered, flexible prompts for contextually relevant examples"""
        
        try:
            from openai import OpenAI
            import os
            
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            
            # AI generates examples based on the specific context
            example_generation_prompt = f"""
            CONTEXT: Student is designing a {building_type} and asked about: {user_topic}
            USER REQUEST: {user_request}
            PROJECT: {project_context}
            
            Your task: Generate a GPT-4 prompt that will produce contextually relevant architectural examples.
            
            The prompt should instruct GPT-4 to:
            1. Find REAL architectural examples of {user_topic} in {building_type}s or similar civic/public buildings
            2. Provide 2-3 specific projects with architect names if possible
            3. For each project, include:
              - Project name
              - Location (city, country)
              - Architect(s) or landscape architect(s)
              - A clickable Markdown link to the official museum website or a reputable architecture source (do not leave blank or incomplete)
            4. Explain WHY these examples work for multi-activity public spaces
            5. Avoid generic residential elements or unrelated famous buildings
            6. Connect to the student's specific design challenge
            7. End with one application question

            
            Example format:
            1. [Project Name](https://example.com) — City, Country. Architect(s). Brief explanation.
            2. ...


            
            Generate ONLY the prompt text that will be sent to GPT-4. Keep it under 200 words.
            Make it specific to this topic and building type.
            """
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": example_generation_prompt}],
                max_tokens=250,
                temperature=0.7
            )

            flexible_prompt = response.choices[0].message.content.strip()
            return flexible_prompt

        except Exception as e:
            print(f"⚠️ Flexible prompt generation failed: {e}")
            # Fallback to a general but context-aware prompt
            return f"""
            Provide examples of {user_topic} specifically in {building_type}s or similar civic/public buildings.

            REQUIREMENTS:
            1. Give 2-3 real architectural examples relevant to {building_type}s
            2. For each, include a link to more information if possible
            3. Focus on {user_topic} in multi-activity public spaces
            4. Explain why these examples work for this building type
            5. Avoid  unrelated examples
            6. Connect to their {building_type} design challenge
            7. For each, include a clickable link, location, architect, and a brief explanation.

            Format: Provide examples with brief explanations and links, then ask how they might apply these approaches.
            Keep under 120 words.
            """
    
    def _analyze_conversation_context(self, state: ArchMentorState) -> Dict[str, Any]:
        """Analyze conversation context for continuity awareness"""
        
        if len(state.messages) < 2:
            return {"type": "initial", "context": None}
        
        # Get recent conversation context (last 4 messages)
        recent_messages = state.messages[-4:]
        user_messages = [msg['content'].lower() for msg in recent_messages if msg.get('role') == 'user']
        assistant_messages = [msg['content'].lower() for msg in recent_messages if msg.get('role') == 'assistant']
        
        current_user_msg = user_messages[-1] if user_messages else ""
        
        # Check for continuation patterns
        context_info = {
            "type": "continuation",
            "previous_examples_given": False,
            "user_requesting_more": False,
            "user_answered_question": False,
            "topic_context": None
        }
        
        # 1. Check if we provided examples recently
        if assistant_messages:
            last_assistant = assistant_messages[-1]
            if any(word in last_assistant for word in ["examples", "approaches", "consider", "precedents"]):
                context_info["previous_examples_given"] = True
        
        # 2. Check if user is asking for more - ENHANCED DETECTION
        if any(phrase in current_user_msg for phrase in [
            "another example", "more example", "give me another", "show me another", "other example",
            "can you give another", "give another", "any other", "other examples", "more examples",
            "additional example", "different example", "what about another"
        ]):
            context_info["user_requesting_more"] = True
        
        # 3. Check if user answered our question
        if assistant_messages and "?" in assistant_messages[-1] and "?" not in current_user_msg:
            context_info["user_answered_question"] = True
        
        # 4. Extract topic context dynamically using AI
        context_info["topic_context"] = self._extract_dynamic_topic_context(user_messages, assistant_messages, state)
        
        print(f"   🔗 Conversation context: {context_info}")
        return context_info

    def _extract_dynamic_topic_context(self, user_messages: List[str], assistant_messages: List[str], state: ArchMentorState) -> str:
        """AI-powered topic extraction with continuity awareness"""
        if not user_messages:
            return state.agent_context.get("current_topic") or "building design"

        # Use the last 10 user and assistant messages for more context
        recent_user_msgs = user_messages[-10:]
        recent_assistant_msgs = assistant_messages[-10:]
        recent_conversation = " ".join(recent_user_msgs + recent_assistant_msgs)
        try:
            topic_extraction_prompt = f"""
            Extract the main architectural topic being discussed from this conversation:
            CONVERSATION: "{recent_conversation}"
            If you see any topic (even if only implied), respond with 1-3 words describing it. If you can't find a topic, try to guess based on context. Only respond 'none' if there is truly no topic at all.
            """
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": topic_extraction_prompt}],
                max_tokens=10,
                temperature=0.3
            )
            extracted_topic = response.choices[0].message.content.strip().lower()
            # If the user message is a follow-up (e.g., starts with "it", "this", "that"), keep previous topic
            if extracted_topic == "none" or any(user_messages[-1].strip().lower().startswith(w) for w in ["it", "this", "that"]):
                return state.agent_context.get("current_topic") or "building design"
            # Otherwise, update the topic
            if extracted_topic and len(extracted_topic) > 2:
                state.agent_context["current_topic"] = extracted_topic
                return extracted_topic
            else:
                return state.agent_context.get("current_topic") or "building design"
        except Exception as e:
            print(f"   ⚠️ AI topic extraction failed: {e}")
            return state.agent_context.get("current_topic") or "building design"





    
    def _user_provided_insights_and_requested_examples(self, state: ArchMentorState) -> bool:
        """Detect if user both shared insights AND requested examples"""
        
        if not state.messages:
            return False
            
        # Get last user message
        last_user_msg = ""
        for msg in reversed(state.messages):
            if msg.get('role') == 'user':
                last_user_msg = msg['content'].lower()
                break
        
        # Check if they provided insights (substantial content) AND requested examples
        has_insights = len(last_user_msg.split()) > 10  # Substantial response
        requests_examples = any(phrase in last_user_msg for phrase in [
            "example", "examples", "show me", "can you give", "provide"
        ])
        
        return has_insights and requests_examples
    
    async def _acknowledge_insights_and_provide_examples(self, state: ArchMentorState, context: Dict[str, Any], gap_type: str) -> Dict[str, Any]:
        """Acknowledge user's insights then provide examples that build on them"""
        
        # Get user's last message to extract their insights
        last_user_msg = ""
        for msg in reversed(state.messages):
            if msg.get('role') == 'user':
                last_user_msg = msg['content']
                break
        
        topic = context.get("topic_context", gap_type.replace('_', ' '))
        building_type = self._extract_building_type_from_context(state)
        
        # Check if visual analysis is available
        visual_context = ""
        visual_insights = state.agent_context.get('visual_insights', {})
        if visual_insights.get('has_visual_analysis'):
            strengths = visual_insights.get('design_strengths', [])
            improvements = visual_insights.get('improvement_opportunities', [])
            elements = visual_insights.get('identified_elements', [])
            
            visual_context = f"""
            VISUAL ANALYSIS AVAILABLE:
            - Design strengths noted: {', '.join(strengths[:2]) if strengths else 'None'}
            - Areas for improvement: {', '.join(improvements[:2]) if improvements else 'None'}
            - Elements identified: {', '.join(elements[:3]) if elements else 'None'}
            """
        
        prompt = f"""
        The student shared insights about {topic} and requested examples. Their message: "{last_user_msg}"
        
        CONTEXT: They're designing a {building_type} and discussing {topic}
        {visual_context}
        
        Create a response that:
        1. ACKNOWLEDGES their insight (especially about visual engagement, relief in dense spaces, etc.)
        2. BUILDS ON their understanding 
        3. PROVIDES 2-3 relevant examples that connect to their insight
        4. ENDS with a question that deepens their thinking
        
        Format:
        "That's an excellent insight about [their point]. [Build on it]. 
        
        Here are examples that demonstrate this:
        [Example 1] - [how it connects to their insight]
        [Example 2] - [how it connects to their insight]
        
        [Thoughtful follow-up question based on their insight]"
        
        Keep under 120 words. Focus on their understanding of visual engagement and spatial relief.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.6
            )
            
            return {
                "knowledge_response": {
                    "response": response.choices[0].message.content.strip(),
                    "has_knowledge": True,
                    "source": "insight_acknowledgment_with_examples"
                },
                "sources": ["User Insight + Examples"],
                "agent": self.name
            }
            
        except Exception as e:
            print(f"⚠️ Insight acknowledgment failed: {e}")
            # Fallback to regular examples
            return await self._provide_additional_examples(state, context, gap_type)
    
    def _extract_building_type_from_context(self, state: ArchMentorState) -> str:
        """Extract building type from project context or user messages, avoiding hardcoded defaults"""
        
        # First check project brief
        if state.current_design_brief:
            brief_lower = state.current_design_brief.lower()
            
            # Expanded building type detection
            building_types = {
                "office": ["office", "workplace", "corporate", "coworking"],
                "school": ["school", "university", "educational", "campus", "classroom"],
                "hospital": ["hospital", "medical", "healthcare", "clinic", "health center"],
                "library": ["library", "archive", "reading", "study"],
                "museum": ["museum", "gallery", "exhibition", "cultural center"],
                "retail": ["store", "shop", "retail", "commercial", "mall"],
                "residential": ["housing", "apartment", "residential", "home", "living"],
                "restaurant": ["restaurant", "cafe", "dining", "food service"],
                "community center": ["community center", "civic", "public facility"],
                "industrial": ["factory", "warehouse", "industrial", "manufacturing"],
                "religious": ["church", "temple", "mosque", "religious", "worship"]
            }
            
            for building_type, keywords in building_types.items():
                if any(keyword in brief_lower for keyword in keywords):
                    return building_type
        
        # Check recent user messages for building type clues
        recent_messages = [msg['content'] for msg in state.messages[-3:] if msg.get('role') == 'user']
        combined_text = " ".join(recent_messages).lower()
        
        building_types = {
            "office": ["office", "workplace", "corporate"],
            "school": ["school", "university", "educational"],
            "hospital": ["hospital", "medical", "healthcare"],
            "library": ["library", "study space"],
            "museum": ["museum", "gallery", "exhibition"],
            "retail": ["store", "shop", "retail"],
            "residential": ["housing", "apartment", "home"],
            "restaurant": ["restaurant", "cafe", "dining"],
            "community center": ["community center", "civic center"],
            "industrial": ["factory", "warehouse", "industrial"]
        }
        
        for building_type, keywords in building_types.items():
            if any(keyword in combined_text for keyword in keywords):
                return building_type
        
        # Final fallback - use generic "building" instead of assuming community center
        return "public building"
    
    async def _provide_additional_examples(self, state: ArchMentorState, context: Dict[str, Any], gap_type: str) -> Dict[str, Any]:
        """Provide additional examples while maintaining topic continuity"""
        
        topic = context.get("topic_context", gap_type.replace('_', ' '))
        
        # Extract building type from actual project context, not hardcoded default
        building_type = self._extract_building_type_from_context(state)
        
        print(f"   🔄 Providing additional examples for: {topic}")
        
        # Search for different examples on the same topic
        results = await self.discover_knowledge(f"{topic}_additional", {}, state)
        
        if results:
            return await self.synthesize_knowledge(results, f"{topic}_continuation", state, {})
        else:
            # Use AI to generate additional examples
            prompt = f"""
            The student previously received examples about {topic} in {building_type}s and is asking for additional examples.
            
            CONTEXT: Continue the conversation by providing NEW examples, not repeating previous ones.
            
            Provide 2-3 DIFFERENT examples of {topic} in {building_type}s or similar public buildings.
            Focus on VARIETY - different approaches, scales, or contexts.
            
            Format:
            "Here are additional examples of {topic}:
            
            [New Example 1] - [brief explanation]
            [New Example 2] - [brief explanation]
            
            These demonstrate different approaches to [principle].
            
            Which of these additional approaches interests you most?"
            
            Keep under 120 words. Maintain conversation continuity.
            """
            
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=150,
                    temperature=0.7
                )
                
                return {
                    "knowledge_response": {
                        "response": response.choices[0].message.content.strip(),
                        "has_knowledge": True,
                        "source": "ai_generated_additional_examples"
                    },
                    "sources": ["AI Generated Additional Examples"],
                    "agent": self.name
                }
                
            except Exception as e:
                print(f"⚠️ Additional examples generation failed: {e}")
                return await self.generate_adaptive_response(gap_type, {}, state)
    
    async def _continue_topic_exploration(self, state: ArchMentorState, context: Dict[str, Any], gap_type: str) -> Dict[str, Any]:
        """Continue exploring topic based on user's answer"""
        
        topic = context.get("topic_context", gap_type.replace('_', ' '))
        
        # Get user's last response
        last_user_msg = ""
        for msg in reversed(state.messages):
            if msg.get('role') == 'user':
                last_user_msg = msg['content']
                break
        
        print(f"   💬 Continuing topic exploration based on: {last_user_msg[:50]}...")
        
        # Generate contextually relevant follow-up
        prompt = f"""
        The student was asked about {topic} and responded: "{last_user_msg}"
        
        CONTEXT: Continue the educational conversation by building on their response.
        
        Based on their answer, provide:
        1. Brief acknowledgment of their choice/interest
        2. Deeper insight into that specific aspect
        3. ONE follow-up question to deepen their understanding
        
        Format:
        "That's an interesting perspective on [their choice]. [Deeper insight about their selection]. 
        
        [Follow-up question to explore deeper]"
        
        Keep under 80 words. Build on their response, don't start over.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=120,
                temperature=0.6
            )
            
            return {
                "knowledge_response": {
                    "response": response.choices[0].message.content.strip(),
                    "has_knowledge": True,
                    "source": "contextual_topic_exploration"
                },
                "sources": ["Contextual Topic Exploration"],
                "agent": self.name
            }
            
        except Exception as e:
            print(f"⚠️ Topic exploration continuation failed: {e}")
            return await self.generate_adaptive_response(gap_type, {}, state)
    
    async def _generate_flexible_synthesis_prompt(self, gap_type: str, building_type: str, project_context: str, combined_knowledge: str, user_request: str) -> str:
        """Generate AI-powered synthesis prompts for multi-source knowledge"""
        
        try:
            from openai import OpenAI
            import os
            
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            
            synthesis_generation_prompt = f"""
            CONTEXT: Student designing {building_type} asked about: {gap_type.replace('_', ' ')}
            USER REQUEST: {user_request}
            AVAILABLE KNOWLEDGE: Multiple sources about this topic
            
            Generate a GPT-4 prompt for synthesizing relevant information from multiple sources.
            
            The prompt should instruct GPT-4 to:
            1. Extract approaches/examples relevant to {building_type}s from the provided sources
            2. Focus on {gap_type.replace('_', ' ')} in multi-activity public spaces
            3. Synthesize 2-3 key approaches that work for this building type
            4. Explain WHY these approaches are effective for {building_type}s
            5. Avoid generic or residential examples
            6. End with application question for their specific project
            
            Generate ONLY the prompt text. Keep under 200 words.
            Make it specific to synthesizing information for this building type and topic.
            """
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": synthesis_generation_prompt}],
                max_tokens=250,
                temperature=0.7
            )
            
            flexible_synthesis_prompt = response.choices[0].message.content.strip()
            return flexible_synthesis_prompt
            
        except Exception as e:
            print(f"⚠️ Flexible synthesis prompt generation failed: {e}")
            # Fallback to context-aware synthesis prompt
            return f"""
            Synthesize information about {gap_type.replace('_', ' ')} from the provided sources, focusing on {building_type}s.
            
            KNOWLEDGE SOURCES: {combined_knowledge}
            
            REQUIREMENTS:
            1. Extract 2-3 key approaches relevant to {building_type}s
            2. Focus on {gap_type.replace('_', ' ')} in multi-activity public spaces  
            3. Explain why these approaches work for this building type
            4. Avoid residential or generic examples
            5. Connect to their {building_type} design
            
            Format: Synthesize approaches with explanations, then ask how they might apply these.
            Keep under 100 words.
            """
    
    async def provide_knowledge(self, state: ArchMentorState, analysis_result: Dict, gap_type: str) -> AgentResponse:
        """Provide knowledge that encourages thinking rather than passive acceptance - now returns AgentResponse"""
        
        print(f"\n📚 {self.name} providing knowledge with cognitive protection...")
        
        # Get user's actual question
        user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
        user_input = user_messages[-1] if user_messages else ""
        
        if not user_input:
            fallback_response = self._generate_fallback_knowledge()
            return self._convert_to_agent_response(fallback_response, state, analysis_result, gap_type)
        
        building_type = self._extract_building_type_from_context(state)
        project_context = state.current_design_brief
        
        # DETECT KNOWLEDGE REQUEST PATTERNS
        #0108-before: knowledge_pattern = self._analyze_knowledge_request(user_input, gap_type, state)
        knowledge_pattern = self._analyze_knowledge_request(user_input, gap_type, state)
        
        # 3107 ADDED: Handle legitimate example requests properly
        if knowledge_pattern["type"] == "legitimate_example_request":
            print(f"📚 Legitimate example request detected - providing examples")
            response_result = await self._provide_focused_examples(state, user_input, gap_type)
            return self._convert_to_agent_response(response_result, state, analysis_result, gap_type)
        #0108-added for 5 min message requirement   
        # Handle premature example requests (cognitive offloading protection)
        if knowledge_pattern["type"] == "premature_example_request":
            print(f"🛡️ Cognitive protection: Example request too early")
            response_result = await self._generate_premature_example_response(user_input, building_type, project_context)
            return self._convert_to_agent_response(response_result, state, analysis_result, gap_type)
        
        if knowledge_pattern["type"] == "direct_answer_seeking":
            response_result = await self._generate_thinking_prompt(user_input, building_type, project_context)
            return self._convert_to_agent_response(response_result, state, analysis_result, gap_type)
        
        # Use AI to generate knowledge that encourages thinking
        prompt = f"""
        You are an architectural mentor who provides knowledge in a way that encourages thinking, not passive acceptance.
        
        STUDENT QUESTION: "{user_input}"
        BUILDING TYPE: {building_type}
        PROJECT: {project_context}
        KNOWLEDGE GAP: {gap_type}
        
        Your response should:
        1. Provide relevant information but frame it as a thinking prompt
        2. Present multiple perspectives or trade-offs
        3. Ask the student to consider implications
        4. Connect to their specific project context
        5. End with a question that requires their reasoning
        6. Avoid giving a single "correct" answer
        
        For example, if they ask about "sustainable materials":
        "Sustainable materials present interesting trade-offs. Bamboo grows quickly but requires specific climate conditions. Reclaimed wood has character but may have structural limitations. Cross-laminated timber is strong but requires careful detailing.
        
        For your {building_type} project, consider: What's your priority - environmental impact, cost, or aesthetics? How does your choice affect the overall design strategy?
        
        What factors are most important for your specific context?"
        
        Give a knowledge-rich response that encourages thinking:
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.3
            )
            
            ai_response = response.choices[0].message.content.strip()
            print(f"📚 AI-generated knowledge response: {ai_response[:100]}...")
            
            response_result = {
                "agent": self.name,
                "response_text": ai_response,
                "response_type": "thinking_prompt_knowledge",
                "knowledge_gap_addressed": gap_type,
                "building_type": building_type,
                "user_input_addressed": user_input,
                "knowledge_pattern": knowledge_pattern,
                "sources": []
            }
            
            # Add cognitive flags to the original response result for backward compatibility
            cognitive_flags = self._extract_cognitive_flags(response_result, state, gap_type)
            response_result["cognitive_flags"] = cognitive_flags
            
            # Convert to standardized AgentResponse format
            return self._convert_to_agent_response(response_result, state, analysis_result, gap_type)
            
        except Exception as e:
            print(f"⚠️ AI response generation failed: {e}")
            fallback_response = self._generate_fallback_knowledge(user_input, building_type)
            return self._convert_to_agent_response(fallback_response, state, analysis_result, gap_type)
    
    def _convert_to_agent_response(self, response_result: Dict, state: ArchMentorState, analysis_result: Dict, gap_type: str) -> AgentResponse:
        """Convert the original response to AgentResponse format while preserving all data"""
        
        # Calculate enhancement metrics
        enhancement_metrics = self._calculate_enhancement_metrics(response_result, state, analysis_result, gap_type)
        
        # Convert cognitive flags to standardized format
        cognitive_flags = self._extract_cognitive_flags(response_result, state, gap_type)
        cognitive_flags_standardized = self._convert_cognitive_flags(cognitive_flags)
        
        # Create standardized response while preserving original data
        response = ResponseBuilder.create_knowledge_response(
            response_text=response_result.get("response_text", ""),
            sources_used=response_result.get("sources", []),
            cognitive_flags=cognitive_flags_standardized,
            enhancement_metrics=enhancement_metrics,
            quality_score=response_result.get("quality_score", 0.5),
            confidence_score=response_result.get("confidence_score", 0.5),
            metadata={
                # Preserve all original data for backward compatibility
                "original_response_result": response_result,
                "knowledge_gap_addressed": response_result.get("knowledge_gap_addressed", ""),
                "building_type": response_result.get("building_type", ""),
                "user_input_addressed": response_result.get("user_input_addressed", ""),
                "knowledge_pattern": response_result.get("knowledge_pattern", {}),
                "analysis_result": analysis_result,
                "gap_type": gap_type,
                "cognitive_flags": cognitive_flags  # Original format
            }
        )
        
        return response
    
    def _calculate_enhancement_metrics(self, response_result: Dict, state: ArchMentorState, analysis_result: Dict, gap_type: str) -> EnhancementMetrics:
        """Calculate cognitive enhancement metrics for domain expertise"""
        
        response_type = response_result.get("response_type", "")
        knowledge_pattern = response_result.get("knowledge_pattern", {})
        building_type = response_result.get("building_type", "")
        
        # Cognitive offloading prevention score
        # Higher score if using thinking prompts or cognitive protection
        cognitive_protection_strategies = ["thinking_prompt_knowledge", "premature_example_response"]
        cop_score = 0.8 if response_type in cognitive_protection_strategies else 0.4
        
        # Deep thinking engagement score
        # Higher score if response encourages thinking and reasoning
        thinking_encouragement = "?" in response_result.get("response_text", "")
        dte_score = 0.9 if thinking_encouragement else 0.5
        
        # Knowledge integration score
        # Higher score if knowledge is contextualized to the project
        has_project_context = bool(response_result.get("building_type") and response_result.get("user_input_addressed"))
        ki_score = 0.8 if has_project_context else 0.3
        
        # Scaffolding effectiveness score
        # Higher score if providing structured knowledge with examples
        has_sources = len(response_result.get("sources", [])) > 0
        scaffolding_score = 0.9 if has_sources else 0.5
        
        # Learning progression score
        # Based on knowledge gap type and response quality
        gap_complexity = len(gap_type.split("_"))  # More complex gaps indicate progression
        learning_progression = min(gap_complexity * 0.2, 1.0)
        
        # Metacognitive awareness score
        # Higher score if response encourages self-reflection
        metacognitive_indicators = ["consider", "think about", "reflect", "evaluate"]
        response_text = response_result.get("response_text", "").lower()
        metacognitive_score = 0.8 if any(indicator in response_text for indicator in metacognitive_indicators) else 0.4
        
        # Overall cognitive score
        overall_score = (cop_score + dte_score + ki_score + scaffolding_score + learning_progression + metacognitive_score) / 6
        
        # Scientific confidence
        # Based on response quality and knowledge pattern analysis
        response_quality = response_result.get("quality_score", 0.5)
        pattern_confidence = 0.8 if knowledge_pattern.get("cognitive_risk") == "low" else 0.6
        scientific_confidence = (response_quality + pattern_confidence) / 2
        
        return EnhancementMetrics(
            cognitive_offloading_prevention_score=cop_score,
            deep_thinking_engagement_score=dte_score,
            knowledge_integration_score=ki_score,
            scaffolding_effectiveness_score=scaffolding_score,
            learning_progression_score=learning_progression,
            metacognitive_awareness_score=metacognitive_score,
            overall_cognitive_score=overall_score,
            scientific_confidence=scientific_confidence
        )
    
    def _extract_cognitive_flags(self, response_result: Dict, state: ArchMentorState, gap_type: str) -> List[str]:
        """Extract cognitive flags from the response and knowledge context"""
        
        flags = []
        response_type = response_result.get("response_type", "")
        knowledge_pattern = response_result.get("knowledge_pattern", {})
        
        # Add flags based on response type
        if response_type == "thinking_prompt_knowledge":
            flags.append("deep_thinking_encouraged")
        elif response_type == "premature_example_response":
            flags.append("cognitive_offloading_detected")
        elif response_type == "legitimate_example_request":
            flags.append("knowledge_integration")
        
        # Add flags based on knowledge pattern
        cognitive_risk = knowledge_pattern.get("cognitive_risk", "low")
        if cognitive_risk == "high":
            flags.append("cognitive_offloading_detected")
        elif cognitive_risk == "low":
            flags.append("scaffolding_provided")
        
        # Add flags based on knowledge gap type
        if "technical" in gap_type:
            flags.append("knowledge_integration")
        elif "conceptual" in gap_type:
            flags.append("deep_thinking_encouraged")
        
        # Add engagement flag if user is actively seeking knowledge
        user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
        if len(user_messages) > 0:
            flags.append("engagement_maintained")
        
        return flags
    
    def _convert_cognitive_flags(self, cognitive_flags: List[str]) -> List[CognitiveFlag]:
        """Convert cognitive flags to standardized format"""
        
        flag_mapping = {
            "deep_thinking_encouraged": CognitiveFlag.DEEP_THINKING_ENCOURAGED,
            "scaffolding_provided": CognitiveFlag.SCAFFOLDING_PROVIDED,
            "cognitive_offloading_detected": CognitiveFlag.COGNITIVE_OFFLOADING_DETECTED,
            "engagement_maintained": CognitiveFlag.ENGAGEMENT_MAINTAINED,
            "knowledge_integration": CognitiveFlag.KNOWLEDGE_INTEGRATION,
            "learning_progression": CognitiveFlag.LEARNING_PROGRESSION,
            "metacognitive_awareness": CognitiveFlag.METACOGNITIVE_AWARENESS
        }
        
        converted_flags = []
        for flag in cognitive_flags:
            if flag in flag_mapping:
                converted_flags.append(flag_mapping[flag])
            else:
                # Default to knowledge integration for unknown flags
                converted_flags.append(CognitiveFlag.KNOWLEDGE_INTEGRATION)
        
        return converted_flags
    
    #0108 state added for 5 min message requirement
    def _analyze_knowledge_request(self, user_input: str, gap_type: str, state: ArchMentorState = None) -> Dict[str, Any]:
        """Analyze the type of knowledge request to prevent cognitive offloading"""
        
        analysis = {
            "type": "standard_knowledge_request",
            "cognitive_risk": "low",
            "indicators": []
        }
        
        #3107-ADDED FOR EXAMPLE REQUESTS
        user_input_lower = user_input.lower()
        
        # ENHANCED: Better detection of legitimate example requests
        example_request_keywords = [
            "example", "examples", "precedent", "precedents", "case study", "case studies",
            "project", "projects", "show me", "can you give", "can you provide", "provide",
            "inspiration", "references", "similar projects", "ideas", "real project", "built project"
        ]
        
        # Check if this is a legitimate example request
        is_example_request = any(keyword in user_input_lower for keyword in example_request_keywords)
        
        if is_example_request:
            # 0108- addedCheck cognitive offloading protection (minimum 5 messages required)
            if state and hasattr(state, 'messages'):
                message_count = len([msg for msg in state.messages if msg.get('role') == 'user'])
                if message_count < 5:
                    analysis["type"] = "premature_example_request"
                    analysis["cognitive_risk"] = "high"
                    analysis["indicators"].append(f"Example request too early (only {message_count} messages, need 5+)")
                    analysis["cognitive_protection"] = "active"
                    return analysis
            


            # This is a legitimate example request - should provide examples
            analysis["type"] = "legitimate_example_request"
            analysis["cognitive_risk"] = "low"
            analysis["indicators"].append("Legitimate example request detected")
            return analysis
        


        # PATTERN 1: Direct answer seeking (but NOT example requests)
        direct_patterns = [
            "what is the", "what are the", "tell me the", 
            "what should I", "what do I need", "the answer is", "the solution is"
        ]
        
        if any(pattern in user_input_lower for pattern in direct_patterns):
            analysis["type"] = "direct_answer_seeking"
            analysis["cognitive_risk"] = "high"
            analysis["indicators"].append("Direct answer seeking detected")
        
        # PATTERN 2: Passive acceptance indicators
        passive_patterns = [
            "okay", "sure", "fine", "whatever", "I guess",
            "that works", "good enough"
        ]
        
        if any(pattern in user_input_lower for pattern in passive_patterns):
            analysis["type"] = "passive_acceptance"
            analysis["cognitive_risk"] = "high"
            analysis["indicators"].append("Passive acceptance detected")
        
        return analysis
    
    async def _generate_thinking_prompt(self, user_input: str, building_type: str, project_context: str) -> Dict[str, Any]:
        """Generate a dynamic thinking prompt instead of a direct answer"""
        
        prompt = f"""
        Generate a dynamic, contextual thinking prompt for an architecture student who is asking for a direct answer.
        
        CONTEXT:
        - Student's Question: "{user_input}"
        - Building Type: {building_type}
        - Project Context: {project_context}
        
        REQUIREMENTS:
        1. Acknowledge their specific question/concern
        2. Explain why thinking through it is valuable
        3. Ask ONE specific question that will guide their thinking
        4. Make it relevant to their {building_type} project
        5. Use a warm, encouraging tone
        6. Keep it under 150 words
        7. Avoid generic templates - be specific to their question
        
        Generate a dynamic thinking prompt:
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=120,
                temperature=0.7
            )
            
            response_text = response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"⚠️ Thinking prompt generation failed: {e}")
            # Fallback to contextual template
            response_text = f"""
**🤔 Let's think about this together**

I notice you're asking about {user_input.lower()}, but let's explore this more deeply. The best architectural solutions come from understanding the underlying principles.

**Instead of giving you the answer, let's consider:**

What specific challenge are you facing with {user_input.lower()} in your {building_type} project, and what have you already considered about this aspect?

*This will help you develop your own reasoning and understanding.*
"""
        
        return {
            "agent": self.name,
            "response_text": response_text,
            "response_type": "thinking_prompt",
            "knowledge_gap_addressed": "thinking_development",
            "building_type": building_type,
            "user_input_addressed": user_input,
            "cognitive_protection": "active"
        }
    #0108-added for 5 min message requirement
    async def _generate_premature_example_response(self, user_input: str, building_type: str, project_context: str) -> Dict[str, Any]:
        """Generate response for premature example requests (cognitive offloading protection)"""
        
        response_text = f"""
**🤔 Let's build your understanding first**

I understand you're looking for examples of {user_input.lower().split('examples')[0].strip()}, but let's take a step back. The best learning happens when we understand the underlying principles first.

**Before diving into examples, let's explore:**

1. **What specific aspect** of {user_input.lower().split('examples')[0].strip()} are you most curious about?

2. **What challenges** are you facing in your {building_type} project that make you think you need examples?

3. **What have you already considered** about this topic? What's your current understanding?

4. **What's your design goal?** How do you envision this fitting into your overall project?

**The goal is to help you develop your own reasoning and understanding, not just show you what others have done.**

*What's the most challenging part of this topic for you right now?*

*Note: After you've explored the concepts more deeply (in a few more messages), I'll be happy to provide specific examples to support your learning.*
"""
        
        return {
            "agent": self.name,
            "response_text": response_text,
            "response_type": "cognitive_protection_response",
            "knowledge_gap_addressed": "premature_example_request",
            "building_type": building_type,
            "user_input_addressed": user_input,
            "cognitive_protection": "active",
            "protection_reason": "premature_example_request"
        }
    
    def _generate_fallback_knowledge(self, user_input: str = "", building_type: str = "project") -> Dict[str, Any]:
        """Generate fallback knowledge when AI fails"""
        
        if not user_input:
            return {
                "agent": self.name,
                "response_text": "I'd be happy to help you with your architectural project. What specific aspect would you like to learn more about?",
                "response_type": "fallback_knowledge",
                "knowledge_gap_addressed": "general_inquiry",
                "building_type": building_type,
                "user_input_addressed": "general inquiry"
            }
        
        # Simple template-based fallback
        return {
            "agent": self.name,
            "response_text": f"I can help you with {user_input.lower()} in your {building_type} project. What specific aspects would you like to explore?",
            "response_type": "fallback_knowledge",
            "knowledge_gap_addressed": "general_guidance",
            "building_type": building_type,
            "user_input_addressed": user_input
        }
    
    async def _provide_focused_examples(self, state: ArchMentorState, user_input: str, gap_type: str) -> Dict[str, Any]:
        """Provide AI-powered, focused responses that directly address the user's specific question"""
        
        building_type = self._extract_building_type_from_context(state)
        project_context = state.current_design_brief
        
        #310 ADDED-RETRIEVAL STRATEGY
        print(f"📚 Implementing KNOWLEDGE RETRIEVAL PIPELINE for: {user_input}")
        
        # STEP 1: QUERY ANALYSIS
        # Extract architectural concepts from user input
        user_topic = self._extract_topic_from_user_input(user_input)
        print(f"   🎯 Extracted topic: {user_topic}")
        
        # STEP 2: RETRIEVAL STRATEGY
        # First try database search
        print(f"   🔍 Searching database for: {user_topic}")
        knowledge_results = await self.discover_knowledge(user_topic, {}, state)
        
        # If database search is insufficient, use web search
        if not knowledge_results or len(knowledge_results) < 2:
            print(f"   🌐 Database insufficient, searching web for: {user_topic}")
            web_results = await self.search_web_for_knowledge(user_topic, state)
            if web_results:
                knowledge_results.extend(web_results)
                print(f"   🌐 Found {len(web_results)} web results")
        
        # STEP 3: SYNTHESIS ALGORITHM
        if knowledge_results:
            print(f"   🔧 Synthesizing {len(knowledge_results)} knowledge sources")
            return await self.synthesize_knowledge(knowledge_results, user_topic, state, {})
        else:
            print(f"   ⚠️ No knowledge found, using AI generation")
            # Use AI to generate examples when no knowledge is found
            return await self._generate_ai_examples(user_input, building_type, project_context, user_topic)
    
    def _extract_topic_from_user_input(self, user_input: str) -> str:
        """Extract the main architectural topic from user input"""
        
        # Common architectural topics
        topic_keywords = {
            "flexible spaces": ["flexible", "flexibility", "adaptable", "multi-use"],
            "lighting": ["light", "lighting", "daylight", "illumination"],
            "circulation": ["circulation", "flow", "movement", "path"],
            "accessibility": ["access", "accessible", "universal design"],
            "sustainability": ["sustainable", "green", "environmental", "eco"],
            "materials": ["material", "finish", "texture", "surface"],
            "structure": ["structure", "structural", "support", "frame"],
            "acoustics": ["acoustic", "sound", "noise", "audio"],
            "ventilation": ["ventilation", "air", "breathing", "fresh air"],
            "shading": ["shade", "shading", "sun protection", "overhang"],
            "community spaces": ["community", "social", "gathering", "public"],
            "office design": ["office", "workplace", "work", "desk"],
            "open plan": ["open plan", "open space", "open office"],
            #3107 ADDED MORE 
            "private spaces": ["private", "quiet", "focus", "individual"],
            "adaptive reuse": ["adaptive reuse", "adaptive", "reuse", "renovation", "retrofit", "conversion", "repurposing"],
            "energy efficiency": ["energy", "efficient", "efficiency", "thermal", "insulation"],
            "natural ventilation": ["natural ventilation", "cross ventilation", "passive cooling"],
            "daylighting": ["daylighting", "daylight", "natural light", "sunlight"],
            "passive design": ["passive", "passive design", "passive solar"],
            "biophilic design": ["biophilic", "nature", "natural elements", "green walls"],
            "universal design": ["universal design", "inclusive design", "accessibility"],
            "modular design": ["modular", "modular design", "prefabricated", "prefab"],
            "smart building": ["smart", "intelligent", "automation", "technology"],
            "historic preservation": ["historic", "preservation", "heritage", "conservation"],
            "urban design": ["urban", "city", "street", "public space"],
            "landscape architecture": ["landscape", "garden", "outdoor", "green space"],
            "interior design": ["interior", "furniture", "furnishings", "spatial design"],
            "parametric design": ["parametric", "algorithmic", "computational", "digital fabrication"],
            "prefabrication": ["prefabrication", "prefab", "modular construction", "off-site"],
            "mass timber": ["mass timber", "cross laminated timber", "clt", "wood construction"],
            "net zero": ["net zero", "zero energy", "carbon neutral", "sustainable"],
            "green building": ["green building", "leed", "sustainable building", "eco-friendly"]
        }
        
        user_input_lower = user_input.lower()
        
        # Find the most specific topic match (prioritize longer/more specific terms first)
        # Sort topics by specificity (longer topic names first)
        sorted_topics = sorted(topic_keywords.items(), key=lambda x: len(x[0]), reverse=True)
        
        # Check all topics for matches
        for topic, keywords in sorted_topics:
            if any(keyword in user_input_lower for keyword in keywords):
                return topic
        
        # If no specific topic found, extract from user input
        words = user_input_lower.split()
        # Look for architectural terms
        architectural_terms = ["space", "design", "building", "room", "area", "zone", "layout"]
        for word in words:
            if word in architectural_terms:
                return f"{word} design"
        
        # Default to the gap_type if nothing specific found
        return user_input_lower.replace(" ", "_")
    
    async def _generate_ai_examples(self, user_input: str, building_type: str, project_context: str, topic: str) -> Dict[str, Any]:
        """Generate AI-powered examples when no knowledge is found - Enhanced for contextual relevance"""

        # Extract the actual topic from user input more dynamically
        dynamic_topic = self._extract_dynamic_topic_from_context(user_input, building_type, project_context)
        
        # Check if user specifically asked for buildings using flexible detection
        building_request_detected = is_building_request(user_input)
        
        building_requirement = ""
        if building_request_detected:
            building_requirement = """
        7. IMPORTANT: The student specifically asked for BUILDING examples. Only provide examples of actual buildings or structures that have been converted/adapted. Do NOT include landscape projects, parks, urban spaces, or outdoor projects.
        """
        
        # Enhanced prompt for better examples
        prompt = f"""
        Provide specific architectural examples for this student's request:
        
        STUDENT REQUEST: "{user_input}"
        BUILDING TYPE: {building_type}
        SPECIFIC TOPIC: {dynamic_topic}
        PROJECT CONTEXT: {project_context}
        
        REQUIREMENTS:
        1. Focus on {dynamic_topic} specifically, not generic architectural concepts
        2. Provide 2-3 examples that are directly relevant to {building_type}s or similar public buildings
        3. Each example should demonstrate {dynamic_topic} in a way that connects to the student's context
        4. Include project names, architects, and locations where possible
        5. Explain WHY these examples work for {dynamic_topic} in {building_type} contexts
        6. Avoid generic examples - be specific to the topic and building type
        7. If the topic involves facade design, shading, or Nordic climate considerations, prioritize examples from Nordic countries or similar climates
        8. For community centers, focus on examples that show how the design serves diverse user groups
        9. Include specific technical details about how the {dynamic_topic} was implemented{building_requirement}
        
        FORMAT:
        **Example 1: [Project Name]**
        [Brief description of how this project specifically addresses {dynamic_topic}]
        Why it works: [Specific reason relevant to {building_type} design]
        
        **Example 2: [Project Name]**
        [Brief description of how this project specifically addresses {dynamic_topic}]
        Why it works: [Specific reason relevant to {building_type} design]
        
        Keep it under 250 words and focus on practical, actionable examples that directly relate to {dynamic_topic}.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.4
            )
            
            ai_response = response.choices[0].message.content.strip()
            print(f"📚 AI-generated contextual examples for {dynamic_topic}: {ai_response[:100]}...")
            
            return {
                "agent": self.name,
                "response_text": ai_response,
                "response_type": "ai_generated_examples",
                "knowledge_gap_addressed": dynamic_topic,
                "examples_provided": 1,
                "building_type": building_type,
                "user_input_addressed": user_input,
                "topic_specific": True,
                "sources": ["AI Generated Examples"]
            }
            
        except Exception as e:
            print(f"⚠️ AI example generation failed: {e}")
            # Final fallback
            return {
                "agent": self.name,
                "response_text": f"I'd be happy to help you explore {dynamic_topic} for your {building_type} project! To provide the most relevant guidance, could you tell me what specific aspect of {dynamic_topic} you're most interested in understanding?",
                "response_type": "fallback_examples",
                "knowledge_gap_addressed": dynamic_topic,
                "building_type": building_type,
                "user_input_addressed": user_input,
                "sources": []
            }
    
    def _extract_dynamic_topic_from_context(self, user_input: str, building_type: str, project_context: str) -> str:
        """Extract the most relevant topic from user input and context, avoiding hardcoded topics"""
        
        # Analyze user input for specific topics
        input_lower = user_input.lower()
        
        # Look for specific architectural topics mentioned
        architectural_topics = {
            "lighting": ["light", "lighting", "daylight", "natural light", "illumination", "windows"],
            "circulation": ["circulation", "flow", "movement", "path", "route", "access"],
            "materials": ["material", "materials", "finish", "construction", "timber", "concrete", "steel"],
            "sustainability": ["sustainable", "green", "environment", "energy", "eco", "climate"],
            "accessibility": ["accessible", "access", "universal", "barrier", "inclusive"],
            "spatial_organization": ["space", "spatial", "layout", "organization", "arrangement"],
            "structural": ["structure", "structural", "beam", "column", "frame", "load"],
            "acoustics": ["acoustic", "sound", "noise", "audio", "echo"],
            "thermal": ["thermal", "heating", "cooling", "insulation", "temperature"],
            "cultural": ["cultural", "heritage", "identity", "community", "local"],
            "adaptive_reuse": ["adaptive", "reuse", "renovation", "conversion", "existing"],
            "connection": ["connection", "link", "relationship", "adjacency", "interface"],
            "modern_addition": ["modern", "addition", "new", "contemporary", "extension"]
        }
        
        # Find the most specific topic mentioned
        for topic, keywords in architectural_topics.items():
            if any(keyword in input_lower for keyword in keywords):
                return topic
        
        # If no specific topic found, extract from context
        if "connection" in input_lower or "relationship" in input_lower:
            return "connection_details"
        elif "old" in input_lower and "new" in input_lower:
            return "adaptive_reuse_interface"
        elif "truss" in input_lower or "beam" in input_lower:
            return "structural_integration"
        elif "example" in input_lower or "project" in input_lower:
            # Extract what they're asking for examples of
            words = input_lower.split()
            for i, word in enumerate(words):
                if word in ["examples", "example", "projects", "project"] and i + 1 < len(words):
                    return words[i + 1]  # Return the topic they want examples of
        
        # Default to a general topic based on building type
        return f"{building_type}_design_principles"
    
    async def _provide_technical_knowledge(self, state: ArchMentorState, user_input: str, gap_type: str) -> Dict[str, Any]:
        """Provide technical knowledge and requirements"""
        
        building_type = self._extract_building_type_from_context(state)
        
        # Generate technical response
        response_text = f"Here are the key technical requirements for {gap_type} in {building_type} projects:\n\n"
        
        # Add specific technical information based on gap type
        if "accessibility" in gap_type.lower():
            response_text += "**ADA Requirements:**\n"
            response_text += "• Door widths: Minimum 32 inches clear opening\n"
            response_text += "• Corridor widths: Minimum 44 inches for wheelchair passage\n"
            response_text += "• Ramp slopes: Maximum 1:12 ratio\n"
            response_text += "• Accessible parking: 1 space per 25 total spaces\n\n"
        
        elif "lighting" in gap_type.lower():
            response_text += "**Lighting Standards:**\n"
            response_text += "• Natural light: Minimum 2% daylight factor\n"
            response_text += "• Artificial lighting: 30-50 foot-candles for general areas\n"
            response_text += "• Emergency lighting: Required in all occupied spaces\n"
            response_text += "• Energy efficiency: LED fixtures recommended\n\n"
        
        elif "circulation" in gap_type.lower():
            response_text += "**Circulation Requirements:**\n"
            response_text += "• Main corridors: Minimum 6 feet width\n"
            response_text += "• Secondary corridors: Minimum 4 feet width\n"
            response_text += "• Exit paths: Clear and unobstructed\n"
            response_text += "• Stair widths: Minimum 44 inches\n\n"
        
        elif "sustainability" in gap_type.lower():
            response_text += "**Sustainability Standards:**\n"
            response_text += "• Energy Efficiency: LEED certification requirements\n"
            response_text += "• Water Conservation: Low-flow fixtures, rainwater harvesting\n"
            response_text += "• Materials: Locally sourced, recycled content materials\n"
            response_text += "• Waste Reduction: Construction waste management plans\n"
            response_text += "• Indoor Air Quality: Low-VOC materials, adequate ventilation\n\n"
        
        elif "energy" in gap_type.lower():
            response_text += "**Energy Efficiency Requirements:**\n"
            response_text += "• Building Envelope: High-performance insulation and air sealing\n"
            response_text += "• HVAC Systems: Energy Star rated equipment\n"
            response_text += "• Lighting: LED fixtures with occupancy sensors\n"
            response_text += "• Renewable Energy: Solar panels, geothermal systems\n"
            response_text += "• Energy Modeling: Required for code compliance\n\n"
        
        elif "ventilation" in gap_type.lower():
            response_text += "**Ventilation Requirements:**\n"
            response_text += "• Natural Ventilation: Minimum 5% of floor area as operable windows\n"
            response_text += "• Mechanical Ventilation: ASHRAE 62.1 standards for indoor air quality\n"
            response_text += "• Cross-Ventilation: Windows on opposite sides for air flow\n"
            response_text += "• Stack Effect: High and low openings for natural convection\n"
            response_text += "• Ventilation Rates: 15-20 air changes per hour for occupied spaces\n\n"
        
        elif "shading" in gap_type.lower():
            response_text += "**Solar Shading Requirements:**\n"
            response_text += "• Overhangs: Minimum 2-3 feet for south-facing windows\n"
            response_text += "• Louvers: Adjustable or fixed louvers for east/west facades\n"
            response_text += "• Vegetation: Deciduous trees for seasonal shading\n"
            response_text += "• Awnings: Retractable or fixed awnings for flexibility\n"
            response_text += "• Solar Angles: Design for summer solstice sun angles\n\n"
        
        elif "climate" in gap_type.lower():
            response_text += "**Climate-Responsive Design Requirements:**\n"
            response_text += "• Thermal Mass: Appropriate materials for heat storage and release\n"
            response_text += "• Ventilation: Natural and mechanical ventilation strategies\n"
            response_text += "• Shading: Solar protection and daylight control\n"
            response_text += "• Orientation: Building placement for optimal solar exposure\n"
            response_text += "• Insulation: Climate-appropriate R-values\n"
            response_text += "• Materials: Climate-appropriate material selection\n\n"
        
        else:
            response_text += f"**{gap_type.title()} Standards:**\n"
            response_text += "• Follow local building codes\n"
            response_text += "• Consider industry best practices\n"
            response_text += "• Ensure safety and functionality\n"
            response_text += "• Meet accessibility requirements\n\n"
        
        response_text += f"These requirements ensure your {building_type} project meets current standards and provides a safe, functional environment. Would you like me to elaborate on any specific aspect?"
        
        return {
            "agent": self.name,
            "response_text": response_text,
            "response_type": "technical_knowledge",
            "knowledge_gap_addressed": gap_type,
            "building_type": building_type,
            "user_input_addressed": user_input[:100] + "..." if len(user_input) > 100 else user_input
        }
    
    async def _provide_general_knowledge(self, state: ArchMentorState, user_input: str, gap_type: str) -> Dict[str, Any]:
        """Provide general knowledge and guidance"""
        
        building_type = self._extract_building_type_from_context(state)
        
        response_text = f"Let me provide you with comprehensive information about {gap_type} in {building_type} projects:\n\n"
        
        # Search for relevant knowledge
        try:
            knowledge_results = await self.discover_knowledge(gap_type, {}, state)
            knowledge_results = self.deduplicate_and_rank(knowledge_results)
            
            if knowledge_results:
                response_text += f"**Key Principles of {gap_type.title()}:**\n\n"
                
                for i, result in enumerate(knowledge_results[:2], 1):
                    content = result.get('content', '')
                    response_text += f"{i}. {content[:150]}...\n\n"
                
                response_text += f"**Application in {building_type.title()} Projects:**\n"
                response_text += f"• Consider the specific needs of your {building_type} users\n"
                response_text += f"• Integrate {gap_type} into your overall design strategy\n"
                response_text += f"• Balance functionality with aesthetic considerations\n"
                response_text += f"• Ensure compliance with relevant standards\n\n"
            else:
                response_text += f"**Understanding {gap_type.title()}:**\n"
                response_text += f"{gap_type.title()} is a crucial aspect of {building_type} design that focuses on creating functional, accessible, and user-friendly spaces. It involves considering how people will interact with and move through your design.\n\n"
                response_text += f"**Key Considerations:**\n"
                response_text += f"• User needs and preferences\n"
                response_text += f"• Functional requirements\n"
                response_text += f"• Safety and accessibility\n"
                response_text += f"• Integration with overall design\n\n"
        
        except Exception as e:
            print(f"   ⚠️ Error in knowledge discovery: {e}")
            response_text += f"**Understanding {gap_type.title()}:**\n"
            response_text += f"{gap_type.title()} is essential for creating effective {building_type} designs. It involves understanding user needs, functional requirements, and how to integrate these elements into your overall design strategy.\n\n"
        
        response_text += f"Would you like me to explore any specific aspect of {gap_type} or provide examples of how it's been successfully implemented in similar projects?"
        
        return {
            "agent": self.name,
            "response_text": response_text,
            "response_type": "general_knowledge",
            "knowledge_gap_addressed": gap_type,
            "building_type": building_type,
            "user_input_addressed": user_input[:100] + "..." if len(user_input) > 100 else user_input
        }

    def create_improvement_overview(self, improvement_areas: List[str], state: ArchMentorState) -> Dict[str, Any]:
        """Create overview of improvement areas for student to choose from"""
        
        building_type = self._extract_building_type_from_context(state)
        
        area_descriptions = {
            "Accessibility Guidance": "Ensuring universal access and inclusive design principles",
            "Spatial Thinking Support": "Optimizing space organization, flow, and circulation patterns", 
            "Brief Clarification": "Developing more detailed program requirements and user needs",
            "Public Space Consideration": "Enhancing community interaction and social dynamics",
            "Program Clarification": "Defining functional zones and activity relationships"
        }
        
        overview_text = f"I've identified several improvement opportunities for your {building_type} design:\n\n"
        
        for i, area in enumerate(improvement_areas, 1):
            description = area_descriptions.get(area, f"Developing {area.lower()} aspects")
            overview_text += f"{i}. **{area}**: {description}\n"
        
        overview_text += f"\nEach area offers valuable enhancement potential for your design."
        
        return {
            "response": overview_text,
            "has_knowledge": True,
            "response_type": "improvement_overview",
            "areas_identified": improvement_areas
        }
    
    async def discover_knowledge(self, gap_type: str, analysis_result: Dict, state: ArchMentorState) -> List[Dict]:
        """Multi-strategy knowledge discovery for creativity and hidden patterns"""
        
        all_results = []
        
        # STRATEGY 1: Context-aware concept extraction
        conceptual_queries = await self.generate_conceptual_queries(gap_type, analysis_result, state)
        
        for query in conceptual_queries:
            results = self.knowledge_manager.search_knowledge(query, n_results=2)
            if results:
                for r in results:
                    r['discovery_method'] = f'conceptual: {query}'
                all_results.extend(results)
        
        # STRATEGY 2: Analogical reasoning - find patterns from other domains
        analogical_queries = self.generate_analogical_queries(gap_type, analysis_result, state)
        
        for query in analogical_queries:
            results = self.knowledge_manager.search_knowledge(query, n_results=2)
            if results:
                for r in results:
                    r['discovery_method'] = f'analogical: {query}'
                all_results.extend(results)
        
        # STRATEGY 3: Problem decomposition - break down complex issues
        decomposed_queries = self.decompose_problem_into_queries(gap_type, analysis_result, state)
        
        for query in decomposed_queries:
            results = self.knowledge_manager.search_knowledge(query, n_results=2)
            if results:
                for r in results:
                    r['discovery_method'] = f'decomposed: {query}'
                all_results.extend(results)
        
        # STRATEGY 4: Cross-domain pattern matching
        if self.domain == "architecture":
            cross_domain_queries = self.generate_cross_domain_queries(gap_type, analysis_result, state)
            for query in cross_domain_queries:
                results = self.knowledge_manager.search_knowledge(query, n_results=1)
                if results:
                    for r in results:
                        r['discovery_method'] = f'cross_domain: {query}'
                    all_results.extend(results)
        
        # Remove duplicates and rank by relevance
        unique_results = self.deduplicate_and_rank(all_results)
        
        print(f"   🔍 Discovery strategies found {len(unique_results)} unique sources")
        return unique_results[:5]  # Top 5 most relevant
    
    async def generate_conceptual_queries(self, gap_type: str, analysis_result: Dict, state: ArchMentorState) -> List[str]:
        """Generate conceptually rich search queries using AI"""
        
        context = {
            "gap_type": gap_type,
            "building_type": analysis_result.get('text_analysis', {}).get('building_type', 'building'),
            "design_brief": state.current_design_brief,
            "domain": self.domain,
            "student_level": state.student_profile.skill_level
        }
        
        prompt = f"""
        Generate 3-4 creative search queries to find relevant knowledge for this design challenge:
        
        CONTEXT:
        - Learning gap: {gap_type.replace('_', ' ')}
        - Project: {context['design_brief'][:200]}
        - Building type: {context['building_type']}
        - Domain: {context['domain']}
        - Student level: {context['student_level']}
        
        Generate queries that:
        1. Capture the ESSENCE of the problem (not just keywords)
        2. Look for PRINCIPLES and PATTERNS (not just facts)
        3. Consider RELATED CONCEPTS and CONNECTIONS
        4. Think about UNDERLYING ISSUES and ROOT CAUSES
        
        Format: Return only the query terms, one per line, no explanations.
        Focus on concepts that might exist in any architecture/design knowledge base.
        
        Examples of good conceptual queries:
        - "spatial organization principles"
        - "user experience design patterns"
        - "accessibility universal design"
        - "lighting natural daylighting strategies"
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.7
            )
            
            queries = [q.strip() for q in response.choices[0].message.content.strip().split('\n') if q.strip()]
            print(f"   🧠 Generated conceptual queries: {queries}")
            return queries[:4]
            
        except Exception as e:
            print(f"   ⚠️ AI query generation failed: {e}")
            # Fallback to rule-based queries
            return self.fallback_conceptual_queries(gap_type, context)
    
    def fallback_conceptual_queries(self, gap_type: str, context: Dict) -> List[str]:
        """Fallback conceptual queries when AI fails - COVER MORE TOPICS"""
        
        conceptual_map = {
            "accessibility_awareness": ["universal design principles", "accessibility standards", "inclusive design"],
            "spatial_thinking_support": ["spatial organization", "circulation patterns", "space planning"],
            "spatial_design": ["space planning", "interior layout", "spatial organization", "room arrangement"],  # NEWd
            "lighting_design": ["natural lighting", "artificial lighting", "daylighting strategies"],  # NEW
            "circulation_design": ["circulation patterns", "pedestrian flow", "movement through space"],  # NEW
            "brief_clarification": ["program requirements", "design process", "project planning"],
            "basic_guidance": ["design fundamentals", "basic principles", f"{context['building_type']} design"],
            "public_space_consideration": ["public space design", "community planning", "social spaces"]
        }
        
        return conceptual_map.get(gap_type, ["design principles", "architectural concepts", context['building_type']])
    
    def generate_analogical_queries(self, gap_type: str, analysis_result: Dict, state: ArchMentorState) -> List[str]:
        """Find analogous situations and patterns from other contexts"""
        
        building_type = analysis_result.get('text_analysis', {}).get('building_type', 'building')
        
        analogical_queries = []
        
        # Functional analogies
        if "community center" in building_type:
            analogical_queries.extend(["social spaces", "gathering places", "public buildings"])
        elif "housing" in building_type:
            analogical_queries.extend(["residential design", "living spaces", "home environments"])
        elif "office" in building_type:
            analogical_queries.extend(["workplace design", "professional environments"])
        
        # Scale analogies
        if "large" in state.current_design_brief or "200" in state.current_design_brief:
            analogical_queries.extend(["large scale design", "complex buildings"])
        
        # Context analogies
        if "nordic" in state.current_design_brief.lower():
            analogical_queries.extend(["cold climate design", "northern architecture"])
        elif "urban" in state.current_design_brief.lower():
            analogical_queries.extend(["urban design", "city planning"])
        
        return analogical_queries[:3]
    
    def decompose_problem_into_queries(self, gap_type: str, analysis_result: Dict, state: ArchMentorState) -> List[str]:
        """Break complex problems into searchable components"""
        
        decomposed_queries = []
        
        if gap_type == "accessibility_awareness":
            decomposed_queries = ["wheelchair access", "door widths", "ramp design", "accessible bathrooms"]
        elif gap_type == "spatial_thinking_support":
            decomposed_queries = ["circulation", "room relationships", "flow patterns", "adjacencies"]
        elif gap_type == "brief_clarification":
            decomposed_queries = ["program analysis", "space requirements", "user needs", "functional zones"]
        elif gap_type == "public_space_consideration":
            decomposed_queries = ["community needs", "social interaction", "public amenities"]
        
        return decomposed_queries[:3]
    
    def generate_cross_domain_queries(self, gap_type: str, analysis_result: Dict, state: ArchMentorState) -> List[str]:
        """Look for patterns from other design domains"""
        
        if gap_type == "spatial_thinking_support":
            return ["navigation design", "wayfinding", "user journey"]
        elif gap_type == "accessibility_awareness":
            return ["inclusive design", "human factors", "ergonomics"]
        elif gap_type == "brief_clarification":
            return ["requirements analysis", "user research", "needs assessment"]
        
        return []
    
    def deduplicate_and_rank(self, results: List[Dict]) -> List[Dict]:
        """Remove duplicates and rank by relevance + discovery method diversity"""
        
        seen_content = set()
        unique_results = []
        
        for result in results:
            content_hash = hash(result['content'][:100])  # First 100 chars as signature
            
            if content_hash not in seen_content:
                seen_content.add(content_hash)
                unique_results.append(result)
        
        # Rank by similarity score (higher is better)
        unique_results.sort(key=lambda x: x.get('similarity', 0), reverse=True)
        
        return unique_results
    
    async def generate_adaptive_response(self, gap_type: str, analysis_result: Dict, state: ArchMentorState) -> Dict[str, Any]:
        """Generate response when no knowledge found - adaptive to user intent"""
        
        # Check if user explicitly requested examples/knowledge
        last_user_message = ""
        for msg in reversed(state.messages):
            if msg.get('role') == 'user':
                last_user_message = msg['content'].lower()
                break
        
        is_knowledge_request = any(word in last_user_message for word in [
            "examples", "example", "precedents", "show me", "provide", "inspiration",
            "references", "case studies", "similar projects", "ideas", "project", "real project", "built project"
        ])
        
        if is_knowledge_request:
            # Extract project context for relevance
            project_context = state.current_design_brief or "architectural project"
            building_type = self._extract_building_type_from_context(state)
            
            prompt = f"""
            CONTEXT: Student is designing a {building_type} and asked for examples about {gap_type.replace('_', ' ')}.
            
            PROJECT: {project_context}
            STUDENT LEVEL: {state.student_profile.skill_level}
            USER REQUEST: {last_user_message}
            
            CRITICAL: Provide examples SPECIFICALLY relevant to {building_type}s or similar civic/public buildings.
            
            Provide CONTEXTUALLY RELEVANT INFORMATION that:
            1. Gives 2-3 specific examples from {building_type}s, libraries, cultural centers, or similar buildings
            2. Explains why these approaches work for multi-activity public spaces
            3. Avoids generic residential examples (fireplaces, living rooms) or unrelated famous buildings
            4. Ends with ONE question connecting to their {building_type} design
            
            Format:
            "Examples of {gap_type.replace('_', ' ')} in {building_type}s and similar buildings:
            
            [Specific relevant example] - [why it works for public spaces]
            [Specific relevant example] - [why it works for public spaces]
            
            How might these approaches work in your {building_type} design?"
            
            Keep under 80 words. Stay contextually relevant to their project type.
            """
        else:
            prompt = f"""
            Guide this architecture student's thinking about {gap_type.replace('_', ' ')}:
            
            CONTEXT:
            - Student level: {state.student_profile.skill_level}
            
            Ask ONE thought-provoking question that hints at what they should consider.
            Keep it under 30 words.
            """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.6
            )
            
            adaptive_response = response.choices[0].message.content.strip()
            
            return {
                "knowledge_response": {
                    "response": adaptive_response,
                    "has_knowledge": True,
                    "source": "adaptive_reasoning"
                },
                "sources": ["AI Generated Examples"],
                "agent": self.name
            }
            
        except Exception as e:
            print(f"⚠️ DOMAIN EXPERT ERROR in generate_adaptive_response: {e}")
            print(f"   User request was: {last_user_message}")
            print(f"   Gap type: {gap_type}")
            return {
                "knowledge_response": {
                    "response": f"I'd like to provide examples for {gap_type.replace('_', ' ')}, but encountered an issue. Let me help with what I can: What specific aspects of {gap_type.replace('_', ' ')} interest you most?",
                    "has_knowledge": False,
                    "source": "error_fallback"
                },
                "sources": ["Error Fallback"],
                "agent": self.name,
                "error": str(e)
            }
    
    async def synthesize_knowledge(self, knowledge_results: List[Dict], gap_type: str, state: ArchMentorState, analysis_result: Dict) -> Dict[str, Any]:
        """Synthesize knowledge with discovery method awareness and clickable links"""
        
        # Group by discovery method for richer synthesis
        methods_used = list(set([r.get('discovery_method', 'direct') for r in knowledge_results]))
        
        # Extract URLs for clickable links
        urls = []
        for result in knowledge_results:
            if result.get('metadata', {}).get('url'):
                urls.append({
                    'title': result.get('metadata', {}).get('title', 'Source'),
                    'url': result.get('metadata', {}).get('url')
                })
        
        combined_knowledge = "\n\n---\n\n".join([
            f"Source ({r.get('discovery_method', 'direct')}): {r['metadata'].get('title', 'Unknown')}\nContent: {r['content']}" 
            for r in knowledge_results
        ])
        
        # Check if user explicitly requested examples/knowledge
        last_user_message = ""
        for msg in reversed(state.messages):
            if msg.get('role') == 'user':
                last_user_message = msg['content'].lower()
                break
        
        is_knowledge_request = any(word in last_user_message for word in [
            "examples", "example", "precedents", "show me", "provide", "inspiration",
            "references", "case studies", "similar projects", "ideas"
        ])
        
        if is_knowledge_request:
            # For knowledge requests, provide actual examples and information with links
            # Check if user specifically asked for buildings using flexible detection
            building_request_detected = is_building_request(last_user_message)
            
            building_filter = ""
            if building_request_detected:
                building_filter = """
            IMPORTANT: The student specifically asked for BUILDING examples. Filter out landscape projects, parks, urban spaces, and outdoor projects. Only include examples that are actual buildings or structures that have been converted/adapted.
            """
            
            synthesis_prompt = f"""
            The student is asking for specific examples and knowledge about {gap_type.replace('_', ' ')}.
            {building_filter}
            
            AVAILABLE KNOWLEDGE: {combined_knowledge}
            
            Create a response that:
            1. Provides specific, concrete examples from the knowledge sources
            2. Includes project names, locations, and brief descriptions where available
            3. Explains the key approaches and strategies used
            4. Makes the content directly relevant to the student's specific context
            5. Varies the response style and approach based on the content available
            6. Keeps it informative and factual
            7. If the student asked for buildings, ONLY include building examples (not landscape/urban projects)
            8. ALWAYS include the web links when available - they are crucial for credibility
            
            AVAILABLE URLS FOR LINKS: {urls}
            
            CRITICAL INSTRUCTIONS:
            - ALWAYS include the web links in markdown format: [Source Name](URL)
            - Keep response under 200 words to avoid cut-off
            - Focus on providing actual information, not questions
            - Make sure to vary the examples and not repeat the same projects
            - If no web results available, clearly state "Based on architectural knowledge" instead of making up links
            - Present 2-3 specific examples with brief explanations
            - Address the student's specific question directly
            """
        else:
            synthesis_prompt = f"""
            Guide the student's thinking about {gap_type.replace('_', ' ')} using available knowledge:
            
            KNOWLEDGE: {combined_knowledge}
            
            Create a response that:
            1. Hints at connections they should explore
            2. Asks questions that lead to discovery of patterns
            3. Encourages them to think about relationships
            4. Varies the approach based on available content
            5. Makes connections to their specific context
            
            Keep it under 60 words. Use questions and thinking prompts.
            """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": synthesis_prompt}],
                max_tokens=250,
                temperature=0.4
            )
            
            synthesized_text = response.choices[0].message.content.strip()
            
            # Add clickable links if available
            if urls and is_knowledge_request:
                links_section = "\n\n**Sources:**\n"
                for url_info in urls[:3]:  # Limit to 3 links
                    links_section += f"- [{url_info['title']}]({url_info['url']})\n"
                synthesized_text += links_section
            
            # Return in the format expected by the orchestrator
            response_type = "knowledge_examples" if is_knowledge_request else "synthesized_knowledge"
            
            return {
                "agent": self.name,
                "response_text": synthesized_text,
                "response_type": response_type,
                "knowledge_gap_addressed": gap_type,
                "building_type": self._extract_building_type_from_context(state),
                "user_input_addressed": last_user_message,
                "synthesis_quality": "multi_strategy",
                "discovery_methods": methods_used,
                "sources": [r.get('metadata', {}).get('source', 'Unknown') for r in knowledge_results[:3]],
                "urls_provided": len(urls) > 0,
                "contextual_variety": True
            }
            
        except Exception as e:
            # Fallback to Socratic approach
            fallback_text = f"Consider the {gap_type.replace('_', ' ')} aspects of your design. What relationships do you notice between user needs and spatial solutions in your project?"
            
            return {
                "agent": self.name,
                "response_text": fallback_text,
                "response_type": "fallback_synthesis",
                "knowledge_gap_addressed": gap_type,
                "building_type": self._extract_building_type_from_context(state),
                "user_input_addressed": last_user_message,
                "error": str(e)
            }
    
    


    async def extract_student_focus_areas(self, student_input: str, analysis_result: Dict, state: ArchMentorState) -> List[Dict[str, str]]:
        """AI-powered extraction of what student wants to discuss - handles ANY topic"""
        
        prompt = f"""
        Extract EXACTLY what this student wants to learn about from their message:
        
        STUDENT SAID: "{student_input}"
        
        CRITICAL RULES:
        1. Focus ONLY on what they explicitly mentioned in their message
        2. Use their exact terminology (e.g., if they said "office spaces", use "office spaces")
        3. Ignore any background project context that doesn't match their question
        4. Be literal and direct - don't interpret or expand beyond their words
        
        Examples:
        - Student says "office spaces" → Extract "Office Spaces"
        - Student says "lighting design" → Extract "Lighting Design"  
        - Student says "sustainable materials" → Extract "Sustainable Materials"
        - Student says "accessibility" → Extract "Accessibility"
        
        Return format (use their exact words):
        - [Their Topic]: [Brief description using their terminology]
        
        If they didn't mention a specific architectural topic, return empty list.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.4
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # Parse AI response into focus areas
            focus_areas = []
            for line in ai_response.split('\n'):
                if ':' in line and line.strip().startswith('-'):
                    parts = line.strip()[1:].split(':', 1)  # Remove '-' and split on first ':'
                    if len(parts) == 2:
                        focus_areas.append({
                            "area": parts[0].strip(),
                            "description": parts[1].strip()
                        })
            
            print(f"🎯 AI extracted focus areas: {[area['area'] for area in focus_areas]}")
            
            # If AI extraction worked, return it
            if focus_areas:
                return focus_areas
            else:
                # Enhanced fallback for edge cases
                return self.enhanced_fallback_extraction(student_input, analysis_result)
                
        except Exception as e:
            print(f"⚠️ AI focus extraction failed: {e}")
            return self.enhanced_fallback_extraction(student_input, analysis_result)

    def enhanced_fallback_extraction(self, student_input: str, analysis_result: Dict) -> List[Dict[str, str]]:
        """Enhanced fallback that handles more diverse topics"""
        
        input_lower = student_input.lower()
        focus_areas = []
        
        # EXPANDED TOPIC DETECTION
        topic_map = {
            # Standard architectural topics
            "space": ("Spatial Design", "Organization and layout of spaces"),
            "layout": ("Spatial Organization", "Arrangement and flow of spaces"),
            "light": ("Lighting Design", "Natural and artificial illumination strategies"),
            "lighting": ("Lighting Design", "Illumination and daylighting approaches"),
            "access": ("Accessibility", "Universal design and inclusive access"),
            "accessible": ("Accessibility", "Universal design principles"),
            "circulation": ("Circulation Design", "Movement patterns and wayfinding"),
            "flow": ("Circulation Flow", "How people move through spaces"),
            "material": ("Material Selection", "Choice and application of building materials"),
            "structure": ("Structural Design", "Building systems and support"),
            "facade": ("Facade Design", "Building envelope and exterior expression"),
            "entrance": ("Entrance Design", "Access points and arrival experience"),
            "sustainability": ("Sustainable Design", "Environmental and energy considerations"),
            "energy": ("Energy Performance", "Building efficiency and consumption"),
            "acoustic": ("Acoustic Design", "Sound and noise management"),
            "sound": ("Acoustic Environment", "Sound quality and control"),
            
            # Program and function
            "program": ("Program Development", "Functional requirements and space allocation"),
            "function": ("Functional Design", "How spaces serve their intended purposes"),
            "community": ("Community Integration", "Connection with local community needs"),
            "user": ("User Experience", "How occupants interact with the space"),
            "comfort": ("Occupant Comfort", "Environmental and physical comfort factors"),
            
            # Advanced topics
            "climate": ("Climate Response", "Adaptation to environmental conditions"),
            "culture": ("Cultural Design", "Culturally responsive architecture"),
            "flexible": ("Adaptive Design", "Flexibility and future adaptability"),
            "adaptive": ("Adaptive Architecture", "Buildings that change over time"),
            "wellness": ("Wellness Design", "Architecture supporting health and wellbeing"),
            "biophilic": ("Biophilic Design", "Integration with natural systems"),
            "nature": ("Nature Integration", "Connecting interior and exterior environments"),
            "innovation": ("Design Innovation", "Creative and experimental approaches"),
            "technology": ("Technology Integration", "Smart building and digital systems"),
            "heritage": ("Heritage Preservation", "Historic building adaptation"),
            "renovation": ("Building Renovation", "Updating and modernizing existing structures"),
            
            # Experience and psychology
            "atmosphere": ("Atmospheric Design", "Creating experiential and emotional qualities"),
            "experience": ("Spatial Experience", "How spaces feel and affect users"),
            "sensory": ("Sensory Design", "Multi-sensory architectural experience"),
            "psychology": ("Environmental Psychology", "Psychological impacts of design"),
            "emotion": ("Emotional Design", "Architecture that evokes specific feelings"),
            "memory": ("Memory and Place", "Creating meaningful and memorable spaces")
        }
        
        # Check for topics in user input
        for keyword, (area_name, description) in topic_map.items():
            if keyword in input_lower:
                focus_areas.append({
                    "area": area_name,
                    "description": description
                })
        
        # If nothing specific found, use cognitive flags as backup
        if not focus_areas:
            cognitive_flags = analysis_result.get('cognitive_flags', [])
            for flag in cognitive_flags[:2]:  # Take top 2 flags
                area_name = flag.replace('needs_', '').replace('_guidance', '').replace('_', ' ').title()
                focus_areas.append({
                    "area": area_name,
                    "description": "Identified learning opportunity"
                })
        
        # Remove duplicates
        seen_areas = set()
        unique_areas = []
        for area in focus_areas:
            if area['area'] not in seen_areas:
                seen_areas.add(area['area'])
                unique_areas.append(area)
        
        return unique_areas[:3]  # Return max 3 areas




    def create_dynamic_overview(self, focus_areas: List[Dict], state: ArchMentorState) -> Dict[str, Any]:
        """Create overview based on what student actually mentioned"""
        
        overview_text = "Based on your input, I see several areas you might want to explore:\n\n"
        
        for i, area in enumerate(focus_areas, 1):
            overview_text += f"{i}. **{area['area']}**: {area['description']}\n"
        
        overview_text += "\nWhich of these resonates most with what you're trying to achieve?"
        
        return {
            "response": overview_text,
            "has_knowledge": True,
            "response_type": "dynamic_overview",
            "focus_areas": focus_areas
        }


    #older version in commented below
    async def provide_targeted_knowledge(self, focus_area: Dict, state: ArchMentorState, analysis_result: Dict) -> Dict[str, Any]:
        """Provide knowledge about the specific area student mentioned - WITH ENHANCED WEB SEARCH"""

        area_name = focus_area["area"].lower()
        print(f"🎯 Providing knowledge about: {area_name}")

        # Generate search queries based on their specific interest
        search_queries = await self.generate_targeted_queries(area_name, state)

        # Search for relevant knowledge in local database
        all_results = []
        for query in search_queries:
            results = self.knowledge_manager.search_knowledge(query, n_results=2)
            if results:
                all_results.extend(results)

        # Get user's request to determine if they want examples/projects
        last_user_message = ""
        for msg in reversed(state.messages):
            if msg.get('role') == 'user':
                last_user_message = msg['content'].lower()
                break

        # Enhanced conditions for triggering web search
        example_request_keywords = ["example", "examples", "project", "projects", "show me", "can you give", "can you provide", "precedent", "case study", "real project", "built project"]
        is_asking_for_examples = any(keyword in last_user_message for keyword in example_request_keywords)
        
        more_info_phrases = [
            "more information", "in depth", "explain more", "tell me more", "details", 
            "deeper", "expand", "elaborate", "more detail"
        ]
        user_requests_more_detail = any(phrase in last_user_message for phrase in more_info_phrases)

        # Check if local results are insufficient
        db_result_is_shallow = False
        if all_results:
            # Check if the top result is too short or generic
            top_result_content = all_results[0].get('content', '')
            db_result_is_shallow = len(top_result_content.split()) < 50

        # ENHANCED WEB SEARCH TRIGGERING CONDITIONS
        should_search_web = (
            not all_results or  # No local results found
            len(all_results) < 2 or  # Too few local results (less than 2)
            is_asking_for_examples or  # User explicitly wants examples/projects
            user_requests_more_detail or  # User wants more detailed information
            db_result_is_shallow or  # Local results are too brief/shallow
            (all_results and "fallback" in all_results[0].get('metadata', {}).get('type', ''))  # Results are just fallback content
        )

        if should_search_web:
            print(f"🌐 Web search triggered for: {area_name}")
            print(f"   Reasons: Examples={is_asking_for_examples}, MoreDetail={user_requests_more_detail}, Shallow={db_result_is_shallow}, FewResults={len(all_results) < 2}")
            
            # Use enhanced web search with better topic targeting
            web_results = await self.search_web_for_knowledge(area_name, state)
            if web_results:
                print(f"   Found {len(web_results)} web results")
                all_results.extend(web_results)
            else:
                print("   Web search returned no results")

        if all_results:
            # Synthesize knowledge about their specific interest
            knowledge_response = await self.synthesize_targeted_knowledge(
                all_results, focus_area, state
            )

            # Add source links to the response
            source_links = []
            sources_list = []
            for result in all_results[:3]:  # Top 3 sources
                source = result['metadata'].get('source', '')
                title = result['metadata'].get('title', 'Source')

                if source and source.startswith('http'):
                    source_links.append(f"• [{title}]({source})")
                    sources_list.append(source)
                elif source:
                    source_links.append(f"• {title}")
                    sources_list.append(title)

            return {
                "agent": self.name,
                "knowledge_response": knowledge_response,
                "confidence": 0.8,
                "sources": sources_list,
                "source_links": source_links,
                "web_search_used": should_search_web
            }
        else:
            # No knowledge found - provide supportive response
            return {
                "agent": self.name,
                "knowledge_response": {
                    "response": f"I'd like to help with {focus_area['area'].lower()}. Can you tell me more specifically what aspect you want to improve?",
                    "has_knowledge": False,
                    "needs_clarification": True
                },
                "confidence": 0.5,
                "sources": [],
                "web_search_used": should_search_web
            }


    def create_exploration_prompt(self, state: ArchMentorState) -> Dict[str, Any]:
        """Create prompt when unclear what student wants"""
        
        return {
            "agent": self.name,
            "knowledge_response": {
                "response": "I'd like to help you improve your design. What specific aspect would you like to focus on?",
                "has_knowledge": False,
                "needs_clarification": True
            },
            "confidence": 0.3,
            "sources": []
        }

    async def generate_targeted_queries(self, area_name: str, state: ArchMentorState) -> List[str]:
        """Generate search queries based on student's specific interest"""
        
        building_context = state.current_design_brief
        
        prompt = f"""
        Generate 3-4 search terms to find relevant architectural knowledge about:
        STUDENT'S INTEREST: {area_name}
        PROJECT CONTEXT: {building_context}
        
        Create search terms that would find relevant architectural/design information.
        Return only the search terms, one per line.
        
        Examples for "central space":
        - community center spatial organization
        - public space layout principles  
        - central gathering area design
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.4
            )
            
            queries = [q.strip() for q in response.choices[0].message.content.strip().split('\n') if q.strip()]
            return queries[:4]
            
        except Exception as e:
            # Fallback queries
            return [area_name, f"{area_name} design", f"architectural {area_name}"]



    async def synthesize_targeted_knowledge(self, knowledge_results: List[Dict], focus_area: Dict, state: ArchMentorState) -> Dict[str, Any]:
        """Synthesize knowledge about student's specific interest - ADAPTIVE APPROACH"""

        combined_knowledge = "\n\n---\n\n".join([
            f"Source: {r['metadata'].get('title', 'Unknown')}\nContent: {r['content']}" 
            for r in knowledge_results
        ])

        # Improved: Robust detection of knowledge/example requests
        last_user_message = ""
        for msg in reversed(state.messages):
            if msg.get('role') == 'user':
                last_user_message = msg['content'].lower()
                break

        # Use regex and fuzzy matching for broader detection
        example_patterns = [
            r"\bexample\b", r"\bexamples\b", r"\bprecedent\b", r"\bprecedents\b",
            r"\bshow me\b", r"\bcan you give\b", r"\bprovide\b", r"\bproject\b",
            r"\bcase study\b", r"\bcase studies\b", r"\bideas\b", r"\breal project\b", r"\bbuilt project\b"
        ]
        is_knowledge_request = any(re.search(pattern, last_user_message) for pattern in example_patterns)

        if is_knowledge_request:
            # User wants actual information/examples - provide educational knowledge
            project_context = state.current_design_brief or "architectural project"
            building_type = self._extract_building_type_from_context(state)
            user_topic = focus_area['area'] if focus_area.get('area', '').lower() != "none" else "museum exhibition lighting"
            synthesis_prompt = await self._generate_flexible_example_prompt(
                user_topic, building_type, project_context, combined_knowledge, last_user_message
            )
        else:
            # Provide factual, concise knowledge only (NO questions instead socratic will do this)
            synthesis_prompt = f"""
            Provide a concise, factual explanation about: {focus_area['area']}

            AVAILABLE KNOWLEDGE: {combined_knowledge}

            Your response should:
            1. Summarize the key principles or facts the student should know
            2. Give practical advice or examples if possible
            3. Do NOT ask any questions or use Socratic prompts

            Keep it under 60 words. Focus on clear, direct knowledge.
            """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": synthesis_prompt}],
                max_tokens=150,
                temperature=0.4
            )

            synthesized_response = response.choices[0].message.content.strip()

            return {
                "response": synthesized_response,
                "has_knowledge": True,
                "focus_area": focus_area['area'],
                "response_type": "educational_guidance"
            }

        except Exception as e:
            return {
                "response": f"Consider the key principles of {focus_area['area'].lower()} for your project. What specific aspect would you like to explore first?",
                "has_knowledge": True,
                "error": str(e)
            }
        
    def _user_is_confused(self, last_user_message: str) -> bool:
        """Detect if user expresses confusion or lack of knowledge."""
        confusion_phrases = [
            "i don't know", "i dont know", "not sure", "no idea", "i don't understand", "i dont understand",
            "what does this have to do", "i am confused", "can you explain", "help me understand", "unclear"
        ]
        return any(phrase in last_user_message for phrase in confusion_phrases)

    async def _clarify_or_explain(self, topic: str, building_type: str) -> Dict[str, Any]:
        """Provide a brief, clear explanation or example for the topic."""
        prompt = f"""
        The student expressed confusion or lack of knowledge about {topic} in {building_type} design.
        Provide a brief, clear explanation (2-3 sentences) of what {topic} means in this context, and give a simple example.
        Avoid asking a question. Be supportive and direct.
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=120,
                temperature=0.4
            )
            return {
                "knowledge_response": {
                    "response": response.choices[0].message.content.strip(),
                    "has_knowledge": True,
                    "source": "clarification"
                },
                "sources": [f"Clarification: {topic}"],
                "agent": self.name
            }
        except Exception as e:
            return {
                "knowledge_response": {
                    "response": f"{topic.title()} in {building_type} design refers to how these spaces are used to enhance the building. For example, a courtyard can bring light and air into the center of a museum.",
                    "has_knowledge": True,
                    "source": "clarification-fallback"
                },
                "sources": [],
                "agent": self.name
            }

    async def provide_direct_answer(self, user_input: str, state: ArchMentorState) -> Dict[str, Any]:
        """Provide a direct, specific answer to the user's question"""
        
        building_type = self._extract_building_type_from_context(state)
        
        # Use AI to generate a direct, helpful response
        prompt = f"""
        You are an expert architectural mentor. Answer this student's question directly and specifically:
        
        STUDENT QUESTION: "{user_input}"
        BUILDING TYPE: {building_type}
        PROJECT: {state.current_design_brief}
        
        Provide a comprehensive, practical answer that:
        1. Directly addresses their specific question
        2. Gives actionable advice and strategies
        3. Explains the architectural principles involved
        4. Provides specific examples or techniques
        5. Is helpful and educational
        
        For example, if they ask about "open space with lots of light while not letting in heat", explain:
        - Specific glazing strategies (low-E coatings, double/triple glazing, spectrally selective glass)
        - Shading techniques (overhangs, louvers, vegetation, awnings)
        - Orientation and window placement strategies
        - Ventilation and air flow considerations
        - Material choices for thermal mass and insulation
        - Integration with overall design strategy
        
        Provide a detailed, helpful response:
        """
        
        try:
            response = self.llm.invoke(prompt)
            direct_answer = response.content.strip()
            print(f"📚 Direct answer generated: {direct_answer[:100]}...")
            
            return {
                "agent": self.name,
                "response_text": direct_answer,
                "response_type": "direct_answer",
                "user_input_addressed": user_input,
                "building_type": building_type
            }
            
        except Exception as e:
            print(f"⚠️ Direct answer generation failed: {e}")
            # Fallback response
            return {
                "agent": self.name,
                "response_text": f"I'd be happy to help you with {user_input}! Let me provide some specific guidance on this topic.",
                "response_type": "fallback",
                "user_input_addressed": user_input,
                "building_type": building_type
            }

async def test_creative_domain_expert():
    print("🧪 Testing Creative Domain Expert Agent...")
    
    state = ArchMentorState()
    state.current_design_brief = "Design a sustainable office building for a tech company"
    state.student_profile.skill_level = "intermediate"
    
    analysis_result = {
        "text_analysis": {"building_type": "office"},
        "cognitive_flags": ["needs_sustainability_guidance"]
    }
    
    expert = DomainExpertAgent("architecture")
    result = await expert.provide_knowledge(state, analysis_result, "sustainability_awareness")
    
    print(f"\n📚 Creative Discovery Results:")
    print(f"   Discovery Method: {result.get('discovery_method')}")
    print(f"   Sources: {result['sources']}")
    print(f"   Confidence: {result['confidence']:.2f}")
    
    if result['knowledge_response']['has_knowledge']:
        print(f"\n💬 Synthesized Knowledge:")
        print(f"   {result['knowledge_response']['response']}")
        
        if 'discovery_methods' in result['knowledge_response']:
            print(f"\n🔍 Discovery Methods Used: {result['knowledge_response']['discovery_methods']}")
    
    return result




if __name__ == "__main__":
    import asyncio
    asyncio.run(test_creative_domain_expert())