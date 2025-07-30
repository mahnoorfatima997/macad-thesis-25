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

class DomainExpertAgent:
    def __init__(self, domain="architecture"):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.domain = domain
        self.name = "domain_expert"
        self.knowledge_manager = KnowledgeManager(domain)
        
        print(f"📚 {self.name} initialized with knowledge base for {domain}")

    # Web search for knowledge if database is empty
    async def search_web_for_knowledge(self, topic: str) -> List[Dict]:
        """Enhanced web search with better architectural query construction"""
        
        try:
            import requests
            from urllib.parse import quote
            import re
            
            # Enhanced search query construction for architecture
            if "example" in topic.lower() or "project" in topic.lower():
                # For example requests, focus on finding real projects
                search_query = f"{topic} architecture projects examples case studies built works"
            else:
                # For general topics, focus on principles and best practices
                search_query = f"{topic} architecture design principles best practices examples"
            
            encoded_query = quote(search_query)
            
            # DuckDuckGo HTML search
            search_url = f"https://duckduckgo.com/html/?q={encoded_query}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            print(f"🌐 Enhanced web search: {search_query}")
            
            response = requests.get(search_url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                results = []
                
                # Pattern to match DuckDuckGo result titles and snippets
                title_pattern = r'<a[^>]*class="result__a"[^>]*>([^<]+)</a>'
                snippet_pattern = r'<a[^>]*class="result__snippet"[^>]*>([^<]+)</a>'
                url_pattern = r'<a[^>]*class="result__a"[^>]*href="([^"]+)"'
                
                titles = re.findall(title_pattern, response.text)
                snippets = re.findall(snippet_pattern, response.text)
                urls = re.findall(url_pattern, response.text)
                
                # Combine results (take up to 4 for better coverage)
                for i in range(min(4, len(titles))):
                    try:
                        title = titles[i] if i < len(titles) else "Web Resource"
                        snippet = snippets[i] if i < len(snippets) else ""
                        url = urls[i] if i < len(urls) else ""
                        
                        # Clean HTML entities
                        title = re.sub(r'&[a-zA-Z]+;', '', title).strip()
                        snippet = re.sub(r'&[a-zA-Z]+;', '', snippet).strip()
                        
                        # Create more substantial content for architectural examples
                        if snippet and len(snippet) > 20:
                            if "example" in topic.lower() or "project" in topic.lower():
                                content = f"Architectural project example: {snippet}. This demonstrates practical approaches to {topic} that can inform design strategies and provide concrete inspiration for similar projects."
                            else:
                                content = f"Research on {topic} reveals: {snippet}. This architectural knowledge provides insights into design principles, best practices, and professional approaches for implementation."
                        else:
                            content = f"Architectural resource about {topic} from {title}. This source provides professional insights into design principles, case studies, and best practices relevant to {topic} in architectural projects."
                        
                        # Extract domain for source tracking
                        domain = ""
                        if url:
                            try:
                                from urllib.parse import urlparse
                                parsed = urlparse(url)
                                domain = parsed.netloc
                            except:
                                domain = "web resource"
                        
                        results.append({
                            "content": content,
                            "metadata": {
                                "title": title,
                                "source": url if url else "Web Search",
                                "domain": domain,
                                "type": "web_search_enhanced",
                                "search_query": search_query,
                                "topic": topic
                            },
                            "similarity": 0.85  # Higher confidence for web results
                        })
                    except Exception as e:
                        print(f"   ⚠️ Error processing result {i}: {e}")
                        continue
                
                if results:
                    print(f"🌐 Found {len(results)} enhanced web search results")
                    return results
                else:
                    print("⚠️ No valid results found in search response")
            
            print("⚠️ No web results found, using enhanced fallback")
            return self._create_enhanced_fallback_knowledge(topic)
            
        except Exception as e:
            print(f"⚠️ Web search failed: {e}")
            return self._create_enhanced_fallback_knowledge(topic)

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
        
        # Match topic to specific knowledge
        topic_lower = topic.lower()
        specific_content = None
        
        for key, content in fallback_knowledge.items():
            if key in topic_lower:
                specific_content = content
                break
        
        # If no specific match, use AI to generate contextually relevant content
        if not specific_content:
            # Use AI to generate flexible, context-aware content
            return self._generate_flexible_knowledge(topic)
        
        return [{
            "content": specific_content,
            "metadata": {
                "title": f"Architectural Principles: {topic.title()}",
                "source": "Architectural Knowledge Base",
                "type": "fallback_knowledge"
            },
            "similarity": 0.7
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









    # def _extract_dynamic_topic_context(self, user_messages: List[str], assistant_messages: List[str]) -> str:
    #     """AI-powered topic extraction - works for ANY architectural topic"""
        
    #     if not user_messages:
    #         return None
            
    #     recent_conversation = " ".join(user_messages[-2:] + assistant_messages[-2:])
        
    #     try:
    #         topic_extraction_prompt = f"""
    #         Extract the main architectural topic being discussed from this conversation:
            
    #         CONVERSATION: "{recent_conversation}"
            
    #         Identify the PRIMARY architectural topic/theme being discussed. Examples:
    #         - If discussing courtyards, airflow, ventilation → "courtyard design"
    #         - If discussing lighting, windows, natural light → "lighting design"  
    #         - If discussing accessibility, doors, ramps → "accessibility"
    #         - If discussing materials, finishes, textures → "materials"
            
    #         Respond with 1-3 words describing the main topic, or "none" if unclear.
    #         """
            
    #         response = self.client.chat.completions.create(
    #             model="gpt-4o",
    #             messages=[{"role": "user", "content": topic_extraction_prompt}],
    #             max_tokens=10,
    #             temperature=0.3
    #         )
            
    #         extracted_topic = response.choices[0].message.content.strip().lower()
            
    #         if extracted_topic != "none" and len(extracted_topic) > 2:
    #             print(f"   🎯 AI extracted topic: {extracted_topic}")
    #             return extracted_topic
    #         else:
    #             return None
                
    #     except Exception as e:
    #         print(f"   ⚠️ AI topic extraction failed: {e}")
    #         return None
    
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
    
    async def provide_knowledge(self, state: ArchMentorState, analysis_result: Dict, gap_type: str) -> Dict[str, Any]:
        """Provide challenging, thought-provoking guidance that pushes the student deeper"""
        
        print(f"\n📚 {self.name} providing challenging knowledge for gap: {gap_type}")
        
        # Get user's actual question
        user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
        user_input = user_messages[-1] if user_messages else ""
        
        if not user_input:
            return self._generate_fallback_knowledge()
        
        building_type = self._extract_building_type_from_context(state)
        project_context = state.current_design_brief
        
        # Use AI to generate challenging, thought-provoking responses
        prompt = f"""
        You are a challenging architectural mentor who pushes students to think deeper about their design decisions. Provide a response that makes them consider trade-offs and implications.
        
        STUDENT QUESTION: "{user_input}"
        BUILDING TYPE: {building_type}
        PROJECT: {project_context}
        
        Your response should:
        1. Challenge their assumptions and make them think critically
        2. Present trade-offs and conflicting priorities they need to consider
        3. Ask probing questions about their design intent
        4. Push them to justify their choices and consider alternatives
        5. Be direct and challenging, not overly supportive
        6. Focus on the deeper architectural implications
        
        For example, if they ask about "open space with light but no heat":
        "You're asking about a fundamental tension in architecture. Every design decision has consequences:
        
        • North-facing windows give consistent light but reduce solar gain in winter
        • Low-E glazing blocks heat but also reduces visible light transmission
        • External shading provides control but adds complexity and maintenance
        
        What's driving your need for this specific balance? How does this choice affect your overall design strategy?"
        
        Give a challenging, thought-provoking response:
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.3
            )
            
            ai_response = response.choices[0].message.content.strip()
            print(f"📚 AI-generated challenging response: {ai_response[:100]}...")
            
            return {
                "agent": self.name,
                "response_text": ai_response,
                "response_type": "challenging_guidance",
                "knowledge_gap_addressed": gap_type,
                "building_type": building_type,
                "user_input_addressed": user_input,
                "sources": []
            }
            
        except Exception as e:
            print(f"⚠️ AI response generation failed: {e}")
            return self._generate_fallback_knowledge(user_input, building_type)
    
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
        
        # Use AI to generate a specific response to their question
        prompt = f"""
        Provide a helpful, specific response to this architecture student's question:
        
        STUDENT QUESTION: "{user_input}"
        BUILDING TYPE: {building_type}
        PROJECT: {project_context}
        TOPIC: {gap_type}
        
        Your response should:
        1. Directly address their specific question (not generic information)
        2. Provide practical, actionable guidance
        3. Include relevant architectural principles and examples
        4. Be specific to their context and building type
        5. Help them understand how to approach their design challenge
        
        For example, if they ask about balancing circulation for play and focus spaces, 
        explain specific strategies for creating zones, transitions, and spatial hierarchies.
        
        Provide a comprehensive, helpful response:
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.3
            )
            
            ai_response = response.choices[0].message.content.strip()
            print(f"📚 AI-generated domain expert response: {ai_response[:100]}...")
            
            return {
                "agent": self.name,
                "response_text": ai_response,
                "response_type": "ai_powered_guidance",
                "knowledge_gap_addressed": gap_type,
                "examples_provided": 1,  # AI response counts as one comprehensive example
                "building_type": building_type,
                "user_input_addressed": user_input[:100] + "..." if len(user_input) > 100 else user_input
            }
            
        except Exception as e:
            print(f"⚠️ AI response generation failed: {e}")
            # Fallback to template-based response
            example_queries = [
                f"{gap_type} {building_type} examples case studies",
                f"successful {building_type} projects {gap_type}",
                f"architectural precedents {gap_type} {building_type}",
                f"built projects {gap_type} {building_type}"
            ]
            
            # Search for examples
            knowledge_results = []
            for query in example_queries:
                try:
                    results = await self.discover_knowledge(gap_type, {}, state)
                    knowledge_results.extend(results)
                except Exception as e:
                    print(f"   ⚠️ Error searching for examples: {e}")
            
            # Deduplicate and rank results
            knowledge_results = self.deduplicate_and_rank(knowledge_results)
            
            # Create focused response
            if knowledge_results:
                response_text = f"I found some excellent examples of {gap_type} in {building_type} projects:\n\n"
                
                for i, result in enumerate(knowledge_results[:3], 1):
                    title = result.get('title', 'Architectural Example')
                    content = result.get('content', '')
                    response_text += f"**{i}. {title}**\n{content[:200]}...\n\n"
                
                response_text += f"These examples demonstrate how {gap_type} can be effectively implemented in {building_type} projects. Would you like me to explore any specific aspect of these examples?"
            else:
                response_text = f"Let me provide you with some key examples of {gap_type} in {building_type} projects:\n\n"
                response_text += f"• **Modern {building_type} with {gap_type}**: Contemporary projects often incorporate {gap_type} through innovative design approaches\n"
                response_text += f"• **Traditional {building_type} with {gap_type}**: Historical precedents show how {gap_type} has been addressed over time\n"
                response_text += f"• **Sustainable {building_type} with {gap_type}**: Green building examples demonstrate environmental considerations\n\n"
                response_text += f"Would you like me to dive deeper into any of these categories or explore specific case studies?"
            
            return {
                "agent": self.name,
                "response_text": response_text,
                "response_type": "focused_examples",
                "knowledge_gap_addressed": gap_type,
                "examples_provided": len(knowledge_results),
                "building_type": building_type,
                "user_input_addressed": user_input[:100] + "..." if len(user_input) > 100 else user_input
            }
    
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
        """Synthesize knowledge with discovery method awareness"""
        
        # Group by discovery method for richer synthesis
        methods_used = list(set([r.get('discovery_method', 'direct') for r in knowledge_results]))
        
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
            # Use AI to generate flexible, contextually relevant synthesis
            project_context = state.current_design_brief or "architectural project"
            building_type = self._extract_building_type_from_context(state)
            
            synthesis_prompt = await self._generate_flexible_synthesis_prompt(
                gap_type, building_type, project_context, combined_knowledge, last_user_message
            )
        else:
            synthesis_prompt = f"""
            Guide the student's thinking about {gap_type.replace('_', ' ')} using available knowledge:
            
            KNOWLEDGE: {combined_knowledge}
            
            Create a response that:
            1. Hints at connections they should explore
            2. Asks questions that lead to discovery of patterns
            3. Encourages them to think about relationships
            
            Keep it under 60 words. Use questions and thinking prompts.
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
            # Fallback to Socratic approach
            return {
                "response": f"Consider the {gap_type.replace('_', ' ')} aspects of your design. What relationships do you notice between user needs and spatial solutions in your project?",
                "has_knowledge": True,
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
            web_results = await self.search_web_for_knowledge(area_name)
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
            # # Regular learning guidance - use Socratic approach ( this is ignoring socratic agent but gives question insted in snthesis)
            # synthesis_prompt = f"""
            # Guide the student's thinking about: {focus_area['area']}

            # AVAILABLE KNOWLEDGE: {combined_knowledge}

            # Provide SOCRATIC GUIDANCE that:
            # 1. Hints at ONE principle they should consider
            # 2. Asks a thought-provoking question that leads to discovery
            # 3. Encourages them to think about relationships

            # Keep it under 60 words. Guide discovery through questions.
            # """

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
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                temperature=0.3
            )
            
            direct_answer = response.choices[0].message.content.strip()
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