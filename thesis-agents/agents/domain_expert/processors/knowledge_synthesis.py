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
            if not knowledge_data:
                return self._create_fallback_synthesis(topic)
            
            # Generate knowledge summary
            knowledge_summary = self._generate_knowledge_summary(topic, knowledge_data)
            
            # Create educational response
            educational_response = self._create_educational_response(topic, knowledge_data, context)
            
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
            
            self.telemetry.log_agent_end("generate_response_internal")
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
            Create an educational response about {topic} in architecture.
            
            Knowledge available: {knowledge.get('summary', 'General architectural knowledge')}
            Context: {context if context else 'General architectural learning'}
            
            Structure the response to:
            1. Introduce the topic clearly
            2. Explain key concepts
            3. Provide practical applications
            4. Include architectural considerations
            
            Keep the tone informative but accessible.
            """
            
            response = await self.client.generate_completion([
                self.client.create_system_message("You are an expert architecture educator."),
                self.client.create_user_message(prompt)
            ])
            
            if response and response.get("content"):
                return response["content"]
            
            return f"Educational information about {topic} in architectural design and practice."
            
        except Exception as e:
            self.telemetry.log_error("_generate_educational_response", str(e))
            return f"Educational content about {topic} in architecture."
    
    async def _generate_practical_response(self, topic: str, knowledge: Dict, context: Dict = None) -> str:
        """Generate practical-focused response."""
        response = f"Practical Applications of {topic}\n\n"
        response += f"In architectural practice, {topic} is commonly applied through:\n\n"
        
        # Add practical examples
        examples = knowledge.get('examples', [])
        if examples:
            for i, example in enumerate(examples[:3], 1):
                response += f"{i}. {example}\n"
        else:
            response += f"• Direct implementation in design projects\n"
            response += f"• Integration with building systems\n"
            response += f"• Coordination with construction processes\n"
        
        response += f"\nWhen implementing {topic}, consider practical factors such as budget, timeline, and constructability."
        
        return response
    
    async def _generate_technical_response(self, topic: str, knowledge: Dict, context: Dict = None) -> str:
        """Generate technical-focused response."""
        response = f"Technical Aspects of {topic}\n\n"
        response += f"From a technical perspective, {topic} involves:\n\n"
        
        # Add technical details
        technical_points = knowledge.get('technical_points', [])
        if technical_points:
            for point in technical_points[:4]:
                response += f"• {point}\n"
        else:
            response += f"• Specification requirements and standards\n"
            response += f"• Performance criteria and testing\n"
            response += f"• Integration with building systems\n"
            response += f"• Code compliance and safety considerations\n"
        
        response += f"\nTechnical implementation of {topic} requires careful coordination with engineering disciplines."
        
        return response
    
    async def _generate_balanced_response(self, topic: str, knowledge: Dict, context: Dict = None) -> str:
        """Generate balanced response covering multiple aspects."""
        response = f"{topic} in Architecture\n\n"
        response += f"{topic} encompasses both design and technical considerations in architectural practice.\n\n"
        
        # Add key aspects
        response += "Key aspects include:\n"
        response += f"• Design integration and aesthetic considerations\n"
        response += f"• Technical requirements and performance criteria\n"
        response += f"• Practical implementation and construction methods\n"
        response += f"• Code compliance and safety requirements\n\n"
        
        response += f"Successful implementation of {topic} requires balancing creative design with technical feasibility."
        
        return response
    
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
    
    def _finalize_knowledge_response(self, response: str) -> str:
        """Finalize the knowledge response."""
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
            'educational_response': f"I can help you learn about {topic} in architectural design.",
            'contextual_insights': [f"{topic} is relevant to architectural practice"],
            'response_package': {'main_content': f"Information about {topic}"},
            'follow_up_questions': [f"Would you like to learn more about {topic}?"],
            'knowledge_gaps': ['Limited information available'],
            'source_count': 0,
            'synthesis_quality': 'basic',
            'synthesis_timestamp': self.telemetry.get_timestamp()
        } 