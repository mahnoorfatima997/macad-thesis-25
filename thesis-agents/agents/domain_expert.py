# agents/domain_expert.py - COMPLETELY REWRITTEN for creativity and flexibility

from typing import Dict, Any, List
import os
from openai import OpenAI
from dotenv import load_dotenv
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from state_manager import ArchMentorState
from knowledge_base.knowledge_manager import KnowledgeManager

class DomainExpertAgent:
    def __init__(self, domain="architecture"):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.domain = domain
        self.name = "domain_expert"
        self.knowledge_manager = KnowledgeManager(domain)
        
        print(f"📚 {self.name} initialized with knowledge base for {domain}")

    # Web search for knowledge if database is empty
    async def search_web_for_knowledge(self, topic: str) -> List[Dict]:
        """Search using DuckDuckGo for Dezeen and ArchDaily articles"""
        
        try:
            import requests
            from urllib.parse import quote
            import re
            
            # DuckDuckGo search with site restriction
            search_query = f"{topic} community center site:dezeen.com OR site:archdaily.com"
            encoded_query = quote(search_query)
            
            # DuckDuckGo HTML search
            search_url = f"https://duckduckgo.com/html/?q={encoded_query}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            print(f"🌐 DuckDuckGo search: {search_query}")
            
            response = requests.get(search_url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                # Extract Dezeen and ArchDaily URLs
                url_pattern = r'href="(https?://(?:www\.)?(?:dezeen|archdaily)\.com[^"]+)"'
                matches = re.findall(url_pattern, response.text)
                
                results = []
                for url in matches[:3]:  # Top 3 results
                    # Clean URL (remove tracking parameters)
                    clean_url = url.split('?')[0]  # Remove query parameters
                    
                    # Extract title from URL
                    url_parts = clean_url.split('/')
                    title_slug = url_parts[-1] if url_parts[-1] else url_parts[-2]
                    title = title_slug.replace('-', ' ').title()
                    
                    site_name = "Dezeen" if "dezeen.com" in clean_url else "ArchDaily"
                    
                    results.append({
                        "content": f"Architectural insight about {topic} from {site_name}: {title}. This resource covers design strategies, case studies, and architectural principles relevant to community center design.",
                        "metadata": {
                            "title": f"{site_name}: {title}",
                            "source": clean_url,
                            "type": "web_search",
                            "site": site_name.lower()
                        },
                        "similarity": 0.8
                    })
                
                if results:
                    print(f"🌐 Found {len(results)} DuckDuckGo results")
                    return results
            
            print("⚠️ No web results found, using fallback")
            return self._create_fallback_knowledge(topic)
            
        except Exception as e:
            print(f"⚠️ DuckDuckGo search failed: {e}")
            return self._create_fallback_knowledge(topic)

    def _create_fallback_knowledge(self, topic: str) -> List[Dict]:
        """Create fallback knowledge when web search fails"""
        
        return [{
            "content": f"Consider key architectural principles for {topic}: flexibility, user experience, accessibility, natural lighting, and community engagement. Focus on how the space can adapt to different functions while maintaining good circulation and visual connections.",
            "metadata": {
                "title": f"Architectural Guidelines: {topic.title()}",
                "source": "https://www.dezeen.com/architecture/",
                "type": "fallback_knowledge"
            },
            "similarity": 0.6
        }]
    
    async def provide_knowledge(self, state: ArchMentorState, analysis_result: Dict[str, Any], gap_type: str) -> Dict[str, Any]:
        """Dynamic knowledge provision based on student's actual interests"""
        
        print(f"\n📚 {self.name} providing knowledge...")
        
        # Get what student actually wants to discuss
        last_message = ""
        # Get what student actually wants to discuss
        last_message = ""
        for msg in reversed(state.messages):
            if msg.get('role') == 'user':
                last_message = msg['content']
                break

        print(f"🎯 Domain Expert processing: {last_message}")

        # AI-powered focus extraction - FORCE it to focus on student's actual topic
        focus_areas = await self.extract_student_focus_areas(last_message, analysis_result, state)

        print(f"🎯 Extracted focus areas: {[area['area'] for area in focus_areas]}")

        # OVERRIDE: If student mentions specific activities, extract those directly
        if any(word in last_message.lower() for word in ["exhibition", "celebration", "event", "activity", "programming"]):
            focus_areas = [{
                "area": "Multi-Functional Space Programming",
                "description": "Designing spaces that can accommodate different activities like exhibitions and celebrations"
            }]
            print(f"🎯 OVERRIDE: Detected activity programming focus")


        if len(focus_areas) > 1:
            # Multiple areas - let student choose
            print(f"🎯 Student mentioned {len(focus_areas)} focus areas")
            overview_response = self.create_dynamic_overview(focus_areas, state)
            
            return {
                "agent": self.name,
                "knowledge_response": overview_response,
                "confidence": 0.8,
                "sources": ["Student input analysis"],
                "discovery_method": "ai_focus_extraction"
            }
        
        elif len(focus_areas) == 1:
            # Single clear focus - provide targeted knowledge
            focus_area = focus_areas[0]
            return await self.provide_targeted_knowledge(focus_area, state, analysis_result)
        
        else:
            # Fallback to asking what they want to explore
            return self.create_exploration_prompt(state)

    def create_improvement_overview(self, improvement_areas: List[str], state: ArchMentorState) -> Dict[str, Any]:
        """Create overview of improvement areas for student to choose from"""
        
        building_type = "community center"  # From your context
        
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
        """Generate response when no knowledge found - still educational"""
        
        prompt = f"""
        No specific knowledge was found in the database, but provide helpful guidance for this architectural design challenge:
        
        CONTEXT:
        - Learning gap: {gap_type.replace('_', ' ')}
        - Project: {state.current_design_brief}
        - Student level: {state.student_profile.skill_level}
        
        Provide:
        1. General principles that apply to this type of challenge
        2. Key questions the student should consider
        3. Approach strategies they could use
        
        Keep it under 100 words and end with a thoughtful question.
        Focus on helping them think through the problem rather than giving direct answers.
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
                "response": adaptive_response,
                "has_knowledge": True,  # Still provides value
                "source_type": "adaptive_reasoning",
                "educational_value": "high"
            }
            
        except Exception as e:
            return {
                "response": f"This is an interesting {gap_type.replace('_', ' ')} challenge. What approaches have you considered so far?",
                "has_knowledge": False,
                "error": str(e)
            }
    
    async def synthesize_knowledge(self, knowledge_results: List[Dict], gap_type: str, state: ArchMentorState, analysis_result: Dict) -> Dict[str, Any]:
        """Synthesize knowledge with discovery method awareness"""
        
        # Group by discovery method for richer synthesis
        methods_used = list(set([r.get('discovery_method', 'direct') for r in knowledge_results]))
        
        combined_knowledge = "\n\n---\n\n".join([
            f"Source ({r.get('discovery_method', 'direct')}): {r['metadata'].get('title', 'Unknown')}\nContent: {r['content']}" 
            for r in knowledge_results
        ])
        
        synthesis_prompt = f"""
        Synthesize knowledge from multiple discovery strategies for an architecture student:
        
        STUDENT CONTEXT:
        - Project: {state.current_design_brief}
        - Skill level: {state.student_profile.skill_level}
        - Learning gap: {gap_type.replace('_', ' ')}
        
        KNOWLEDGE FROM MULTIPLE SOURCES:
        {combined_knowledge}
        
        DISCOVERY METHODS USED: {', '.join(methods_used)}
        
        Create a response that:
        1. Synthesizes insights from different sources
        2. Shows connections and patterns
        3. Adapts complexity to student level
        4. Provides actionable guidance
        5. Maintains educational focus (guide, don't solve)
        
        Under 150 words. Connect the knowledge to their specific project.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": synthesis_prompt}],
                max_tokens=200,
                temperature=0.4
            )
            
            return {
                "response": response.choices[0].message.content.strip(),
                "has_knowledge": True,
                "synthesis_quality": "multi_strategy",
                "discovery_methods": methods_used
            }
            
        except Exception as e:
            # Fallback to simple synthesis
            return {
                "response": f"Based on multiple sources about {gap_type.replace('_', ' ')}: {knowledge_results[0]['content'][:150]}... How might this apply to your design?",
                "has_knowledge": True,
                "error": str(e)
            }
    
    


    async def extract_student_focus_areas(self, student_input: str, analysis_result: Dict, state: ArchMentorState) -> List[Dict[str, str]]:
        """AI-powered extraction of what student wants to discuss - handles ANY topic"""
        
        prompt = f"""
        Extract what this architecture student wants to improve, learn about, or discuss:
        
        STUDENT INPUT: "{student_input}"
        PROJECT CONTEXT: {state.current_design_brief}
        SKILL LEVEL: {state.student_profile.skill_level}
        
        Extract 1-3 focus areas they're interested in. Be responsive to WHATEVER they ask about.
        
        Handle ANY architectural topic, including:
        
        STANDARD TOPICS:
        - Accessibility and universal design
        - Spatial organization and layout
        - Lighting (natural and artificial)
        - Circulation and movement patterns
        - Building envelope and facade design
        - Structural systems and materials
        - Program development and functional zones
        - Site planning and context
        - Sustainability and environmental design
        - Building codes and regulations
        
        ADVANCED/SPECIALIZED TOPICS:
        - Phenomenological experience and atmosphere
        - Cultural and social aspects of design
        - Acoustic design and soundscapes
        - Biophilic and nature-integrated design
        - Adaptive and flexible architecture
        - Historic preservation and renovation
        - Community engagement and participatory design
        - Building performance and post-occupancy evaluation
        - Computational design and parametric modeling
        - Prefabrication and construction methods
        
        CREATIVE/EXPERIMENTAL TOPICS:
        - Sensory design beyond vision
        - Temporal aspects of architecture
        - Psychological impacts of space
        - Innovation in materials and technology
        - Cross-cultural design approaches
        - Architecture for specific populations
        - Climate-responsive design strategies
        - Urban design and city planning connections
        
        For each area they mention, provide:
        - AREA: Specific topic name (use their terminology when possible)
        - DESCRIPTION: What this involves for their project
        
        Examples:
        - Acoustic Design: Creating appropriate sound environments for different activities
        - Material Experience: How users physically and emotionally experience building materials
        - Community Integration: Ensuring the building serves and connects with its neighborhood
        - Adaptive Flexibility: Designing spaces that can change use over time
        - Wellness-Focused Design: Creating environments that support occupant health and wellbeing
        
        IMPORTANT: Only extract areas they ACTUALLY mentioned or strongly implied. 
        Don't add topics they didn't ask about.
        If they ask about something unusual or creative, extract that specific interest.
        
        Return format:
        - [Area Name]: [Description of what this involves]
        
        If you can't identify specific areas, return an empty list.
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
        """Provide knowledge about the specific area student mentioned - WITH WEB SEARCH AND SOURCES"""
        
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
        
        # If no local knowledge found, search web
        if not all_results:
            print(f"🌐 Local knowledge empty, searching web for: {area_name}")
            web_results = await self.search_web_for_knowledge(area_name)
            all_results.extend(web_results)
        
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
            
            # Add sources to response text
            if source_links:
                knowledge_response['response'] += f"\n\n**Sources:**\n" + "\n".join(source_links)
            
            return {
                "agent": self.name,
                "knowledge_response": knowledge_response,
                "confidence": 0.8,
                "sources": sources_list,
                "source_links": source_links
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
                "sources": []
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
        """Synthesize knowledge about student's specific interest"""
        
        combined_knowledge = "\n\n---\n\n".join([
            f"Source: {r['metadata'].get('title', 'Unknown')}\nContent: {r['content']}" 
            for r in knowledge_results
        ])
        
        synthesis_prompt = f"""
        Synthesize knowledge about the student's specific interest:
        
        STUDENT'S FOCUS: {focus_area['area']} - {focus_area['description']}
        PROJECT: {state.current_design_brief}
        
        RELEVANT KNOWLEDGE:
        {combined_knowledge}
        
        Create a response that:
        1. Addresses their specific interest in {focus_area['area']}
        2. Uses the provided knowledge sources
        3. Connects to their project context
        4. Provides actionable insights
        5. Stays focused on what they asked about
        
        Under 150 words. Focus only on their stated interest.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": synthesis_prompt}],
                max_tokens=200,
                temperature=0.4
            )
            
            return {
                "response": response.choices[0].message.content.strip(),
                "has_knowledge": True,
                "focus_area": focus_area['area'],
                "response_type": "targeted_knowledge"
            }
            
        except Exception as e:
            return {
                "response": f"Based on the available information about {focus_area['area'].lower()}: {knowledge_results[0]['content'][:100]}...",
                "has_knowledge": True,
                "error": str(e)
            }
        



# Test the new creative approach
async def test_creative_domain_expert():
    print("🧪 Testing Creative Domain Expert Agent...")
    
    state = ArchMentorState()
    state.current_design_brief = "Design a community center for elderly people in a cold climate"
    state.student_profile.skill_level = "intermediate"
    
    analysis_result = {
        "text_analysis": {"building_type": "community center"},
        "cognitive_flags": ["needs_accessibility_guidance"]
    }
    
    expert = DomainExpertAgent("architecture")
    result = await expert.provide_knowledge(state, analysis_result, "accessibility_awareness")
    
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