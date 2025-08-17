"""
Knowledge synthesis processing module for synthesizing knowledge and generating responses.
"""
from typing import Dict, Any, List, Optional
from ...common import TextProcessor, MetricsCalculator, AgentTelemetry, LLMClient
from state_manager import ArchMentorState


class KnowledgeSynthesisProcessor:
    """
    Processes knowledge synthesis and response generation.
    """
    
    def __init__(self):
        self.telemetry = AgentTelemetry("knowledge_synthesis")
        self.text_processor = TextProcessor()
        self.metrics_calculator = MetricsCalculator()
        self.client = LLMClient()
        
    async def synthesize_knowledge_internal(self, topic: str, knowledge_data: List[Dict], 
                                          context: Dict = None, state: ArchMentorState = None) -> Dict[str, Any]:
        """
        Synthesize knowledge from multiple sources into a coherent response.
        """
        self.telemetry.log_agent_start("synthesize_knowledge_internal")
        
        try:
            # If no knowledge data available, attempt an LLM-generated, context-aware fallback
            if not knowledge_data:
                try:
                    prepared = self._prepare_knowledge_delivery([], 'educational')
                    llm_response = await self._generate_educational_response(
                        topic, prepared, context or {}
                    )
                    # Build a minimal synthesis result package using the LLM output
                    synthesis_result = {
                        'topic': topic,
                        'knowledge_summary': f"Limited information retrieved for {topic} at this moment.",
                        'educational_response': llm_response,
                        'contextual_insights': self._generate_contextual_insights(topic, (context or {}).get('building_type')),
                        'response_package': self._create_response_package(topic, [] , context or {}),
                        'follow_up_questions': self._generate_follow_up_questions(topic, context or {}),
                        'knowledge_gaps': ['Limited source diversity'],
                        'source_count': 0,
                        'synthesis_quality': 'basic',
                        'synthesis_timestamp': self.telemetry.get_timestamp()
                    }
                    self.telemetry.log_agent_end("synthesize_knowledge_internal")
                    return synthesis_result
                except Exception:
                    # Hard fallback if LLM generation fails
                    return self._create_fallback_synthesis(topic)
            
            # Generate knowledge summary
            knowledge_summary = self._generate_knowledge_summary(topic, knowledge_data)
            
            # Decide if user is asking for examples/projects explicitly
            user_wants_examples = False
            try:
                if state and getattr(state, 'messages', None):
                    last_user = next((m.get('content','').lower() for m in reversed(state.messages) if m.get('role')=='user'), '')
                    for kw in [
                        'example','examples','precedent','precedents','case study','case studies',
                        'project','projects','show me','can you give','can you provide','similar projects'
                    ]:
                        if kw in last_user:
                            user_wants_examples = True
                            break
            except Exception:
                pass

            # If examples are requested, produce concise, example-focused response with links
            if user_wants_examples:
                educational_response = self._create_example_focused_response(topic, knowledge_data, context)
            else:
                # Prefer LLM-generated educational response for variety and context-awareness
                prepared_knowledge = self._prepare_knowledge_delivery(knowledge_data, 'educational')
                educational_response = await self._generate_educational_response(topic, prepared_knowledge, context or {})
            
            # Generate contextual insights
            building_type = context.get('building_type') if context else None
            contextual_insights = self._generate_contextual_insights(topic, building_type)
            
            # Create response package
            response_package = self._create_response_package(topic, knowledge_data, context)
            
            # Generate follow-up questions
            follow_up_questions = self._generate_follow_up_questions(topic, context)
            
            # Assess knowledge gaps
            knowledge_gaps = self._assess_knowledge_gaps_from_synthesis(topic, knowledge_data)
            
            synthesis_result = {
                'topic': topic,
                'knowledge_summary': knowledge_summary,
                'educational_response': educational_response,
                'contextual_insights': contextual_insights,
                'response_package': response_package,
                'follow_up_questions': follow_up_questions,
                'knowledge_gaps': knowledge_gaps,
                'source_count': len(knowledge_data),
                'synthesis_quality': self._assess_synthesis_quality(knowledge_data, educational_response),
                'synthesis_timestamp': self.telemetry.get_timestamp()
            }
            
            self.telemetry.log_agent_end("synthesize_knowledge_internal")
            return synthesis_result
            
        except Exception as e:
            self.telemetry.log_error("synthesize_knowledge_internal", str(e))
            return self._create_fallback_synthesis(topic)
    
    async def generate_response_internal(self, topic: str, knowledge_data: List[Dict], 
                                       context: Dict = None, delivery_style: str = 'educational') -> str:
        """
        Generate internal response from synthesized knowledge.
        """
        self.telemetry.log_agent_start("generate_response_internal")
        
        try:
            if not knowledge_data:
                return f"I'd be happy to help you learn about {topic} in architecture. Let me provide you with some fundamental information about this topic."
            
            # Prepare knowledge for delivery
            prepared_knowledge = self._prepare_knowledge_delivery(knowledge_data, delivery_style)
            
            # Generate contextual response based on delivery style
            if delivery_style == 'educational':
                response = await self._generate_educational_response(topic, prepared_knowledge, context)
            elif delivery_style == 'practical':
                response = await self._generate_practical_response(topic, prepared_knowledge, context)
            elif delivery_style == 'technical':
                response = await self._generate_technical_response(topic, prepared_knowledge, context)
            else:
                response = await self._generate_balanced_response(topic, prepared_knowledge, context)
            
            # Optimize response for learning
            optimized_response = self._optimize_for_learning(response, context.get('user_level', 'intermediate') if context else 'intermediate')
            
            # Validate response completeness
            if self._validate_response_completeness(optimized_response):
                final_response = self._finalize_knowledge_response(optimized_response)
            else:
                final_response = self._enhance_incomplete_response(optimized_response, topic)
            
            return final_response
            
        except Exception as e:
            self.telemetry.log_error("generate_response_internal", str(e))
            return f"I apologize, but I encountered an issue while preparing information about {topic}. Let me provide you with some general guidance on this architectural topic."
    
    def _generate_knowledge_summary(self, topic: str, results: List[Dict]) -> str:
        """Generate a comprehensive knowledge summary."""
        try:
            if not results:
                return f"Limited information available about {topic}."
            
            # Extract key information from results
            key_points = []
            for result in results[:5]:  # Use top 5 results
                snippet = result.get('snippet', '')
                if snippet:
                    # Extract the most informative sentence
                    sentences = snippet.split('.')
                    for sentence in sentences:
                        if len(sentence.strip()) > 20:  # Filter out short fragments
                            key_points.append(sentence.strip())
                            break
            
            # Create summary
            if key_points:
                summary = f"Key information about {topic}:\n\n"
                for i, point in enumerate(key_points[:4], 1):
                    summary += f"{i}. {point}.\n"
                
                summary += f"\nThis information covers various aspects of {topic} in architectural practice."
                return summary
            else:
                return f"General information about {topic} is available from multiple architectural sources."
                
        except Exception as e:
            self.telemetry.log_error("_generate_knowledge_summary", str(e))
            return f"Summary of {topic} information."
    
    def _create_educational_response(self, topic: str, knowledge_data: List[Dict], context: Dict = None) -> str:
        """Create an educational response from knowledge data."""
        try:
            if not knowledge_data:
                return f"Let me help you understand {topic} in architecture."
            
            # Determine the educational approach based on context
            building_type = context.get('building_type', 'general') if context else 'general'
            complexity_level = context.get('complexity_level', 'intermediate') if context else 'intermediate'
            
            # Start with an introduction
            response = f"Understanding {topic} in Architecture\n\n"
            
            # Add context-specific introduction
            if building_type != 'general':
                response += f"In {building_type} architecture, {topic} plays a crucial role. "
            
            # Extract and organize key concepts
            key_concepts = self._extract_key_concepts(knowledge_data)
            
            if key_concepts:
                response += "Key concepts include:\n\n"
                for i, concept in enumerate(key_concepts[:4], 1):
                    response += f"{i}. {concept}\n"
                response += "\n"
            
            # Add practical applications
            applications = self._extract_practical_applications(knowledge_data, building_type)
            if applications:
                response += "Practical applications:\n"
                response += applications + "\n\n"
            
            # Add considerations specific to architecture
            response += f"When working with {topic} in architectural design, consider factors such as "
            response += "functionality, aesthetics, sustainability, and user experience."
            
            return response
            
        except Exception as e:
            self.telemetry.log_error("_create_educational_response", str(e))
            return f"Educational information about {topic} in architectural design."

    def _create_example_focused_response(self, topic: str, knowledge_data: List[Dict], context: Dict = None) -> str:
        """Create concise example-focused response with proper Markdown links, completely topic-agnostic."""
        try:
            if not knowledge_data:
                return f"Examples of {topic} in architecture are varied. Would you like me to look for specific projects?"

            # Dynamic topic-based filtering - extract key concepts from the user's topic
            topic_keywords = self._extract_topic_keywords(topic)
            
            # Filter results based on topic relevance, not hardcoded assumptions
            examples = []
            for item in knowledge_data:
                title = item.get('title') or item.get('metadata', {}).get('title', '')
                url = item.get('url') or item.get('metadata', {}).get('url', '')
                snippet = item.get('snippet') or item.get('content', '')
                
                # Skip items without proper URLs
                if not url or 'http' not in url:
                    continue
                
                # Skip items with very short or empty content
                if not title.strip() or not snippet.strip():
                    continue
                
                # Score relevance based on topic keywords, not hardcoded terms
                relevance_score = self._calculate_topic_relevance(title, snippet, topic_keywords)
                
                # Prefer items that are relevant to the user's specific topic
                if relevance_score > 0.2:  # Lower threshold for better coverage
                    examples.append({
                        'title': title.strip()[:80],
                        'url': url.strip(),
                        'snippet': snippet.strip(),
                        'relevance': relevance_score
                    })
                
                if len(examples) >= 8:  # Get more candidates for better filtering
                    break

            # Sort by relevance and take top 3
            examples.sort(key=lambda x: x['relevance'], reverse=True)
            examples = examples[:3]

            if not examples:
                return f"Examples of {topic} in architecture are varied. Would you like me to look for specific projects?"

            # Build clean, properly formatted example list
            lines = []
            lines.append(f"## Examples of {topic}")
            lines.append("")  # Add spacing
            
            for i, example in enumerate(examples, 1):
                title = example['title']
                url = example['url']
                snippet = example['snippet']
                
                # Clean snippet - remove extra whitespace and truncate properly
                clean_snippet = ' '.join(snippet.split())[:120]
                if len(snippet) > 120:
                    clean_snippet += "..."
                
                # Proper Markdown link format: [Title](URL)
                lines.append(f"### {i}. [{title}]({url})")
                lines.append(f"{clean_snippet}")
                lines.append("")  # Add spacing between examples

            # Add a generic, topic-agnostic application prompt
            lines.append("**How could these approaches inform your design process?**")
            
            # Ensure clean formatting
            final_response = "\n".join(lines).strip()
            
            # Validate the response doesn't have weird formatting
            if "##" in final_response and "###" in final_response:
                return final_response
            else:
                # Fallback to simpler format if Markdown is broken
                return self._create_simple_example_response(examples, topic)
            
        except Exception as e:
            self.telemetry.log_error("_create_example_focused_response", str(e))
            return f"Examples of {topic} in architecture are varied. Would you like me to look for specific projects?"
    
    def _create_simple_example_response(self, examples: List[Dict], topic: str) -> str:
        """Create a simple, clean example response without complex Markdown."""
        lines = [f"Examples of {topic}:"]
        lines.append("")
        
        for i, example in enumerate(examples, 1):
            title = example['title']
            url = example['url']
            snippet = example['snippet']
            
            # Clean snippet
            clean_snippet = ' '.join(snippet.split())[:120]
            if len(snippet) > 120:
                clean_snippet += "..."
            
            # Simple format: Title - URL - Description
            lines.append(f"{i}. {title}")
            lines.append(f"   Link: {url}")
            lines.append(f"   {clean_snippet}")
            lines.append("")
        
        lines.append("How could these approaches inform your design process?")
        return "\n".join(lines)
    
    def _extract_topic_keywords(self, topic: str) -> List[str]:
        """Extract meaningful keywords from the user's topic for better filtering."""
        # Remove common architectural words to focus on the specific topic
        common_words = {
            'design', 'architecture', 'building', 'space', 'project', 'the', 'a', 'an', 'and', 'or', 
            'in', 'on', 'at', 'to', 'for', 'of', 'with', 'is', 'are', 'was', 'were', 'be', 'been',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may',
            'might', 'can', 'must', 'shall', 'this', 'that', 'these', 'those', 'it', 'its', 'they',
            'them', 'their', 'we', 'our', 'you', 'your', 'me', 'my', 'i', 'am', 'im'
        }
        
        # Split topic into words and filter
        words = topic.lower().split()
        keywords = []
        
        for word in words:
            # Remove punctuation and clean
            clean_word = word.strip('.,!?;:()[]{}"\'').lower()
            
            # Skip common words and very short words
            if (clean_word not in common_words and 
                len(clean_word) > 2 and 
                clean_word.isalpha()):
                keywords.append(clean_word)
        
        # If no keywords found, use the original topic words (excluding very common ones)
        if not keywords:
            for word in words:
                clean_word = word.strip('.,!?;:()[]{}"\'').lower()
                if clean_word not in {'the', 'a', 'an', 'and', 'or', 'in', 'on', 'at', 'to', 'for', 'of', 'with'}:
                    keywords.append(clean_word)
        
        return keywords[:5]  # Limit to top 5 keywords
    
    def _calculate_topic_relevance(self, title: str, snippet: str, topic_keywords: List[str]) -> float:
        """Calculate how relevant an example is to the user's specific topic."""
        if not topic_keywords:
            return 0.5  # Neutral score if no keywords
        
        text = f"{title} {snippet}".lower()
        
        # Count keyword matches
        matches = sum(1 for keyword in topic_keywords if keyword in text)
        
        # Base relevance score
        relevance = matches / len(topic_keywords)
        
        # Bonus for title matches (more important)
        title_matches = sum(1 for keyword in topic_keywords if keyword in title.lower())
        if title_matches > 0:
            relevance += 0.3
        
        # Bonus for multiple keyword matches
        if matches >= 2:
            relevance += 0.2
        
        # Bonus for exact phrase matches (if topic is a phrase)
        if len(topic_keywords) > 1:
            # Check for 2+ consecutive keywords
            topic_phrase = ' '.join(topic_keywords[:2])
            if topic_phrase in text:
                relevance += 0.3
        
        # Penalty for very generic content
        generic_words = ['architecture', 'design', 'building', 'project', 'space']
        generic_count = sum(1 for word in generic_words if word in text.lower())
        if generic_count >= 3:
            relevance -= 0.1
        
        return max(0.0, min(relevance, 1.0))  # Ensure score is between 0.0 and 1.0
    
    def _generate_contextual_insights(self, topic: str, building_type: str = None) -> List[str]:
        """Generate contextual insights for the topic."""
        try:
            insights = []
            
            # General architectural insights
            insights.append(f"{topic} requires careful consideration of both form and function")
            insights.append(f"Integration with overall design vision is essential for {topic}")
            
            # Building type specific insights
            if building_type:
                type_insights = {
                    'residential': f"In residential projects, {topic} should prioritize comfort and livability",
                    'commercial': f"Commercial applications of {topic} must balance efficiency with user experience",
                    'institutional': f"Institutional use of {topic} requires compliance with specific codes and standards",
                    'industrial': f"Industrial applications of {topic} focus on functionality and safety"
                }
                
                if building_type in type_insights:
                    insights.append(type_insights[building_type])
            
            # Add sustainability insight
            insights.append(f"Sustainable approaches to {topic} can enhance long-term building performance")
            
            return insights[:4]  # Return top 4 insights
            
        except Exception as e:
            self.telemetry.log_error("_generate_contextual_insights", str(e))
            return [f"Consider multiple aspects when implementing {topic} in architectural design"]
    
    def _create_response_package(self, topic: str, knowledge: List[Dict], context: Dict = None) -> Dict[str, Any]:
        """Create a comprehensive response package."""
        try:
            package = {
                'main_content': self._extract_main_content(knowledge),
                'examples': self._format_examples_list(self._extract_examples(knowledge)),
                'key_points': self._extract_key_points(knowledge),
                'related_topics': self._identify_related_topics(topic),
                'practical_tips': self._generate_practical_tips(topic, context),
                'further_reading': self._suggest_further_reading(topic)
            }
            
            return package
            
        except Exception as e:
            self.telemetry.log_error("_create_response_package", str(e))
            return {
                'main_content': f"Information about {topic}",
                'examples': [],
                'key_points': [],
                'related_topics': [],
                'practical_tips': [],
                'further_reading': []
            }

    def _format_examples_list(self, examples: List[str]) -> List[str]:
        """Format example titles or snippets into a concise list."""
        try:
            if not examples:
                return []
            formatted = []
            for ex in examples[:5]:
                if not isinstance(ex, str):
                    continue
                ex = ex.strip()
                if len(ex) > 120:
                    ex = ex[:117] + "..."
                formatted.append(ex)
            return formatted
        except Exception as e:
            self.telemetry.log_error("_format_examples_list", str(e))
            return examples or []
    
    def _generate_follow_up_questions(self, topic: str, context: Dict = None) -> List[str]:
        """Generate relevant follow-up questions."""
        try:
            questions = []
            
            # General follow-up questions
            questions.append(f"Would you like to explore specific applications of {topic}?")
            questions.append(f"Are you interested in the technical aspects of {topic}?")
            
            # Context-specific questions
            if context:
                building_type = context.get('building_type')
                if building_type and building_type != 'general':
                    questions.append(f"How does {topic} apply specifically to {building_type} projects?")
                
                complexity_level = context.get('complexity_level', 'intermediate')
                if complexity_level == 'beginner':
                    questions.append(f"Would you like to see some basic examples of {topic}?")
                elif complexity_level == 'advanced':
                    questions.append(f"Are you interested in advanced techniques for {topic}?")
            
            # Topic-specific questions
            topic_questions = self._generate_topic_specific_questions(topic)
            questions.extend(topic_questions)
            
            return questions[:4]  # Return top 4 questions
            
        except Exception as e:
            self.telemetry.log_error("_generate_follow_up_questions", str(e))
            return [f"Would you like to learn more about {topic}?"]
    
    async def _generate_educational_response(self, topic: str, knowledge: Dict, context: Dict = None) -> str:
        """Generate educational-style response."""
        try:
            prompt = f"""
            Create a clean, educational response about {topic} in architecture.

            Knowledge available: {knowledge.get('summary', 'General architectural knowledge')}
            Context: {context if context else 'General architectural learning'}

            Requirements:
            - Write in clear, flowing paragraphs without markdown headers
            - No ### or ## headers - use natural paragraph breaks instead
            - Introduce the topic clearly
            - Explain key concepts in an accessible way
            - Provide practical applications
            - Include architectural considerations
            - Keep the tone informative but conversational
            - Maximum 300 words

            Format as clean text with paragraph breaks, not markdown.
            """

            response = await self.client.generate_completion([
                self.client.create_system_message("You are an expert architecture educator. Write clean, flowing text without markdown headers."),
                self.client.create_user_message(prompt)
            ])

            if response and response.get("content"):
                # Clean any markdown headers that might have been generated
                clean_response = self._clean_markdown_headers(response["content"])
                return clean_response
            
            return f"Educational information about {topic} in architectural design and practice."
            
        except Exception as e:
            self.telemetry.log_error("_generate_educational_response", str(e))
            return f"Educational content about {topic} in architecture."
    
    async def _generate_practical_response(self, topic: str, knowledge: Dict, context: Dict = None) -> str:
        """Generate practical-focused response."""
        response = f"In architectural practice, {topic} is commonly applied through direct implementation in design projects, "
        response += f"integration with building systems, and coordination with construction processes.\n\n"

        # Add practical examples in paragraph form
        examples = knowledge.get('examples', [])
        if examples:
            response += "Key applications include: "
            response += ", ".join(examples[:3]) + ".\n\n"

        response += f"When implementing {topic}, consider practical factors such as budget, timeline, and constructability."

        return self._clean_markdown_headers(response)
    
    async def _generate_technical_response(self, topic: str, knowledge: Dict, context: Dict = None) -> str:
        """Generate technical-focused response."""
        response = f"From a technical perspective, {topic} involves specification requirements and standards, "
        response += f"performance criteria and testing, integration with building systems, and code compliance considerations.\n\n"

        # Add technical details in paragraph form
        technical_points = knowledge.get('technical_points', [])
        if technical_points:
            response += "Key technical aspects include: " + ", ".join(technical_points[:4]) + ".\n\n"

        response += f"Technical implementation of {topic} requires careful coordination with engineering disciplines."

        return self._clean_markdown_headers(response)
    
    async def _generate_balanced_response(self, topic: str, knowledge: Dict, context: Dict = None) -> str:
        """Generate balanced response covering multiple aspects."""
        response = f"{topic} encompasses both design and technical considerations in architectural practice.\n\n"

        # Add key aspects in paragraph form
        response += "Key aspects include design integration and aesthetic considerations, "
        response += "technical requirements and performance criteria, practical implementation and construction methods, "
        response += "and code compliance and safety requirements.\n\n"

        response += f"Successful implementation of {topic} requires balancing creative design with technical feasibility."

        return self._clean_markdown_headers(response)
    
    # Helper methods for knowledge processing
    
    def _extract_key_concepts(self, knowledge_data: List[Dict]) -> List[str]:
        """Extract key concepts from knowledge data."""
        concepts = []
        for item in knowledge_data[:3]:
            snippet = item.get('snippet', '')
            if snippet:
                # Simple concept extraction
                sentences = snippet.split('.')
                for sentence in sentences[:2]:
                    if len(sentence.strip()) > 15:
                        concepts.append(sentence.strip())
        
        return concepts[:4]
    
    def _extract_practical_applications(self, knowledge_data: List[Dict], building_type: str) -> str:
        """Extract practical applications from knowledge data."""
        applications = []
        
        for item in knowledge_data[:2]:
            snippet = item.get('snippet', '')
            if 'application' in snippet.lower() or 'use' in snippet.lower():
                applications.append(snippet[:100] + "...")
        
        if applications:
            return ' '.join(applications)
        else:
            return f"Applications vary based on specific project requirements and {building_type} context."
    
    def _extract_main_content(self, knowledge: List[Dict]) -> str:
        """Extract main content from knowledge sources."""
        if not knowledge:
            return "General architectural information available."
        
        main_snippets = []
        for item in knowledge[:3]:
            snippet = item.get('snippet', '')
            if snippet:
                main_snippets.append(snippet)
        
        return ' '.join(main_snippets)
    
    def _extract_examples(self, knowledge: List[Dict]) -> List[str]:
        """Extract examples from knowledge sources."""
        examples = []
        
        for item in knowledge:
            snippet = item.get('snippet', '').lower()
            title = item.get('title', '').lower()
            
            if 'example' in snippet or 'case' in snippet or 'project' in title:
                examples.append(item.get('title', 'Example project'))
        
        return examples[:3]
    
    def _extract_key_points(self, knowledge: List[Dict]) -> List[str]:
        """Extract key points from knowledge sources."""
        points = []
        
        for item in knowledge[:4]:
            key_points = item.get('key_points', [])
            if key_points:
                points.extend(key_points[:2])
        
        return points[:5]
    
    def _identify_related_topics(self, topic: str) -> List[str]:
        """Identify related topics."""
        topic_relations = {
            'sustainable design': ['green building', 'energy efficiency', 'LEED certification'],
            'structural systems': ['building materials', 'foundation design', 'seismic design'],
            'building materials': ['construction methods', 'sustainability', 'cost analysis'],
            'space planning': ['circulation design', 'accessibility', 'building codes'],
            'lighting design': ['daylighting', 'electrical systems', 'energy efficiency']
        }
        
        return topic_relations.get(topic.lower(), ['architectural design', 'building performance', 'construction'])
    
    def _generate_practical_tips(self, topic: str, context: Dict = None) -> List[str]:
        """Generate practical tips for the topic."""
        tips = [
            f"Consider {topic} early in the design process",
            f"Coordinate {topic} with other building systems",
            f"Verify {topic} compliance with local codes"
        ]
        
        if context and context.get('building_type'):
            building_type = context['building_type']
            tips.append(f"Adapt {topic} strategies for {building_type} requirements")
        
        return tips
    
    def _suggest_further_reading(self, topic: str) -> List[str]:
        """Suggest further reading resources."""
        return [
            f"Professional standards for {topic}",
            f"Case studies in {topic} implementation",
            f"Research publications on {topic}",
            f"Industry best practices for {topic}"
        ]
    
    def _generate_topic_specific_questions(self, topic: str) -> List[str]:
        """Generate topic-specific follow-up questions."""
        generic_questions = [
            f"What are the current trends in {topic}?",
            f"How does {topic} vary by building type?"
        ]
        
        # Add specific questions based on topic
        if 'sustainable' in topic.lower():
            generic_questions.append("What are the environmental benefits?")
        elif 'structural' in topic.lower():
            generic_questions.append("What are the engineering considerations?")
        elif 'material' in topic.lower():
            generic_questions.append("What are the cost implications?")
        
        return generic_questions[:2]
    
    def _prepare_knowledge_delivery(self, knowledge_data: List[Dict], delivery_style: str) -> Dict[str, Any]:
        """Prepare knowledge for delivery based on style."""
        prepared = {
            'summary': self._generate_knowledge_summary('topic', knowledge_data),
            'examples': self._extract_examples(knowledge_data),
            'key_points': self._extract_key_points(knowledge_data),
            'technical_points': []
        }
        
        # Add style-specific content
        if delivery_style == 'technical':
            prepared['technical_points'] = self._extract_technical_content(knowledge_data)
        elif delivery_style == 'practical':
            prepared['practical_examples'] = self._extract_practical_examples(knowledge_data)
        
        return prepared
    
    def _extract_technical_content(self, knowledge_data: List[Dict]) -> List[str]:
        """Extract technical content from knowledge data."""
        technical_content = []
        
        for item in knowledge_data:
            snippet = item.get('snippet', '').lower()
            if any(word in snippet for word in ['specification', 'standard', 'code', 'requirement']):
                technical_content.append(item.get('snippet', ''))
        
        return technical_content[:3]
    
    def _extract_practical_examples(self, knowledge_data: List[Dict]) -> List[str]:
        """Extract practical examples from knowledge data."""
        examples = []
        
        for item in knowledge_data:
            snippet = item.get('snippet', '').lower()
            if any(word in snippet for word in ['example', 'case', 'project', 'application']):
                examples.append(item.get('snippet', ''))
        
        return examples[:3]
    
    def _optimize_for_learning(self, content: str, user_level: str = 'intermediate') -> str:
        """Optimize content for learning based on user level."""
        if user_level == 'beginner':
            # Add more explanatory content
            if len(content) < 200:
                content += "\n\nThis is a fundamental concept in architecture that affects many aspects of building design."
        elif user_level == 'advanced':
            # Add more technical depth
            content += "\n\nFor advanced applications, consider the integration with other building systems and long-term performance implications."
        
        return content
    
    def _validate_response_completeness(self, response: str) -> bool:
        """Validate if response is complete and informative."""
        return len(response) > 100 and '.' in response
    
    def _clean_markdown_headers(self, text: str) -> str:
        """Clean markdown headers from text."""
        import re

        # Remove markdown headers (### or ##)
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)

        # Remove excessive line breaks
        text = re.sub(r'\n{3,}', '\n\n', text)

        # Clean up any remaining formatting issues
        text = text.strip()

        return text

    def _finalize_knowledge_response(self, response: str) -> str:
        """Finalize the knowledge response."""
        # Clean markdown headers first
        response = self._clean_markdown_headers(response)

        # Ensure proper ending
        if not response.endswith(('.', '!', '?')):
            response += "."

        return response
    
    def _enhance_incomplete_response(self, response: str, topic: str) -> str:
        """Enhance incomplete response with additional content."""
        if len(response) < 100:
            response += f"\n\n{topic} is an important consideration in architectural design that requires careful planning and integration with overall project goals."
        
        return response
    
    def _assess_synthesis_quality(self, knowledge_data: List[Dict], response: str) -> str:
        """Assess the quality of knowledge synthesis."""
        quality_factors = []
        
        # Source diversity
        sources = set(item.get('source', 'unknown') for item in knowledge_data)
        if len(sources) > 2:
            quality_factors.append('diverse_sources')
        
        # Response length and depth
        if len(response) > 300:
            quality_factors.append('comprehensive')
        
        # Content richness
        if len(knowledge_data) > 3:
            quality_factors.append('rich_content')
        
        if len(quality_factors) >= 2:
            return 'high'
        elif len(quality_factors) >= 1:
            return 'medium'
        else:
            return 'basic'
    
    def _assess_knowledge_gaps_from_synthesis(self, topic: str, knowledge_data: List[Dict]) -> List[str]:
        """Assess knowledge gaps from synthesis process."""
        gaps = []
        
        if len(knowledge_data) < 3:
            gaps.append('Limited source diversity')
        
        # Check for content types
        has_examples = any('example' in item.get('snippet', '').lower() for item in knowledge_data)
        has_technical = any('technical' in item.get('snippet', '').lower() for item in knowledge_data)
        
        if not has_examples:
            gaps.append('Practical examples needed')
        if not has_technical:
            gaps.append('Technical details needed')
        
        return gaps
    
    def _create_fallback_synthesis(self, topic: str) -> Dict[str, Any]:
        """Create fallback synthesis when main synthesis fails."""
        return {
            'topic': topic,
            'knowledge_summary': f"General information about {topic} in architecture.",
            'educational_response': (
                f"Let's explore {topic} in your project context. I'll outline key considerations, common pitfalls, and practical next steps you can act on."
            ),
            'contextual_insights': [f"{topic} is relevant to architectural practice"],
            'response_package': {'main_content': f"Information about {topic}"},
            'follow_up_questions': [f"Would you like to learn more about {topic}?"],
            'knowledge_gaps': ['Limited information available'],
            'source_count': 0,
            'synthesis_quality': 'basic',
            'synthesis_timestamp': self.telemetry.get_timestamp()
        } 