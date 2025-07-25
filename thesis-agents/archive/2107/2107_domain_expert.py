# agents/domain_expert.py
from typing import Dict, Any, List
import os
from openai import OpenAI
from dotenv import load_dotenv
import sys

# Add path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from state_manager import ArchMentorState
from knowledge_base.knowledge_manager import KnowledgeManager

load_dotenv()

class DomainExpertAgent:
    def __init__(self, domain="architecture"):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.domain = domain
        self.name = "domain_expert"
        self.knowledge_manager = KnowledgeManager(domain)
        
        print(f"📚 {self.name} initialized with knowledge base for {domain}")
    
    async def provide_knowledge(self, state: ArchMentorState, analysis_result: Dict[str, Any], gap_type: str) -> Dict[str, Any]:
        """Provide domain-specific knowledge based on cognitive gap"""
        
        print(f"\n📚 {self.name} providing knowledge for gap: {gap_type}")
        
        # Generate search query based on gap and context
        search_query = self.generate_search_query(gap_type, analysis_result, state)
        print(f"🔍 Search query: {search_query}")
        
        # Search knowledge base first
        knowledge_results = self.knowledge_manager.search_knowledge(
            search_query, 
            n_results=3, 
            min_similarity=0.05  # Lower better results
        )
        
        if knowledge_results:
            # Synthesize knowledge from database
            print(f"✅ Found {len(knowledge_results)} knowledge sources")
            knowledge_response = await self.synthesize_knowledge(
                knowledge_results, gap_type, state, analysis_result
            )
            confidence = max([r.get('similarity', 0) for r in knowledge_results])
            sources = [r['metadata']['title'] for r in knowledge_results]
        else:
            # No knowledge found - be honest about it
            print("⚠️ No relevant knowledge found in database")
            knowledge_response = {
                "response": f"I don't have specific information about {gap_type.replace('_', ' ')} in my knowledge base. Let's explore this together through questions and your own reasoning.",
                "has_knowledge": False,
                "recommendation": "Use Socratic approach instead"
            }
            confidence = 0.0
            sources = []
        
        return {
            "agent": self.name,
            "gap_addressed": gap_type,
            "knowledge_response": knowledge_response,
            "confidence": confidence,
            "sources": sources,
            "search_query": search_query
        }
    
    # Better search queries

    def generate_search_query(self, gap_type: str, analysis_result: Dict, state: ArchMentorState) -> str:
        """Generate search queries that match your NYC knowledge base"""
        
        # Get context
        building_type = analysis_result.get('text_analysis', {}).get('building_type', 'building')
        
        # Get user's actual question
        last_message = ""
        for msg in reversed(state.messages):
            if msg.get('role') == 'user':
                last_message = msg['content']
                break
        
        # SEARCH FOR WHAT'S ACTUALLY IN YOUR KNOWLEDGE BASE
        
        # Your knowledge base has NYC housing/development reports
        if "accessibility" in last_message.lower() or gap_type == "accessibility_awareness":
            return "housing accessibility requirements"  # NYC housing has accessibility info
        
        if "community center" in building_type.lower():
            return "community center housing development"  # Search for development info
        
        if "ada" in last_message.lower() or "door width" in last_message.lower():
            return "building accessibility standards"
        
        if "confused" in last_message.lower():
            return "housing planning development"  # Your knowledge base topic
        
        # Default searches based on your NYC content
        gap_to_search = {
            "accessibility_awareness": "housing accessibility",
            "spatial_relationships": "housing design planning", 
            "brief_development": "housing development planning",
            "systems_thinking": "housing community planning"
        }
        
        base_query = gap_to_search.get(gap_type, "housing development")
        
        print(f"   🔍 Generated search query: '{base_query}' (targeting NYC housing content)")
        
        return base_query
    
    async def synthesize_knowledge(self, knowledge_results: List[Dict], gap_type: str, state: ArchMentorState, analysis_result: Dict) -> Dict[str, Any]:
        """Synthesize knowledge from search results"""
        
        # Combine knowledge content
        combined_knowledge = "\n\n---\n\n".join([
            f"Source: {r['metadata']['title']}\nContent: {r['content']}" 
            for r in knowledge_results
        ])
        
        sources = [r['metadata']['title'] for r in knowledge_results]
        
        # Get context
        building_type = analysis_result.get('text_analysis', {}).get('building_type', 'building')
        student_level = state.student_profile.skill_level
        
        # Generate contextual response using GPT-4
        synthesis_prompt = f"""
        You are a domain expert providing knowledge to help an {student_level} architecture student.
        
        STUDENT'S PROJECT: {state.current_design_brief}
        BUILDING TYPE: {building_type}
        COGNITIVE GAP: {gap_type.replace('_', ' ')}
        
        RELEVANT KNOWLEDGE FROM DATABASE:
        {combined_knowledge}
        
        TASK: Synthesize this knowledge into a helpful response that:
        1. Directly addresses the cognitive gap ({gap_type.replace('_', ' ')})
        2. Is appropriate for {student_level} level student
        3. Provides specific, actionable guidance
        4. References the sources appropriately
        5. Connects to their specific project context
        6. NEVER hallucinates - only use the provided knowledge
        7. Be honest if the knowledge doesn't fully address the question
        
        Keep response under 150 words and end with a thoughtful question to continue learning.
        
        Format: Start with the knowledge, then ask a question.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a knowledgeable architecture educator. Base your response only on the provided knowledge. Never make up facts. Always cite sources."
                    },
                    {
                        "role": "user", 
                        "content": synthesis_prompt
                    }
                ],
                max_tokens=250,
                temperature=0.3
            )
            
            synthesized_response = response.choices[0].message.content.strip()
            
            return {
                "response": synthesized_response,
                "has_knowledge": True,
                "sources_used": sources,
                "knowledge_confidence": min([r.get('similarity', 0) for r in knowledge_results])
            }
            
        except Exception as e:
            print(f"❌ Knowledge synthesis failed: {e}")
            
            # Fallback response using the raw knowledge
            fallback_response = f"Based on my knowledge about {building_type} projects"
            if sources:
                fallback_response += f" (from {sources[0]})"
            fallback_response += f", here's what I found: {knowledge_results[0]['content'][:200]}..."
            fallback_response += f"\n\nHow does this relate to your specific {building_type} project?"
            
            return {
                "response": fallback_response,
                "has_knowledge": True,
                "sources_used": sources,
                "error": str(e)
            }

# Test function
async def test_domain_expert():
    print("🧪 Testing Domain Expert Agent...")
    
    # Create test state
    state = ArchMentorState()
    state.current_design_brief = "Design affordable housing for middle-class families in Manhattan"
    state.student_profile.skill_level = "intermediate"
    
    # Mock analysis result
    analysis_result = {
        "text_analysis": {"building_type": "housing"},
        "cognitive_flags": ["needs_brief_clarification"]
    }
    
    # Test domain expert
    expert = DomainExpertAgent("architecture")
    result = await expert.provide_knowledge(state, analysis_result, "brief_development")
    
    print(f"\n📚 Domain Expert Results:")
    print(f"   Search Query: '{result['search_query']}'")
    print(f"   Sources Found: {result['sources']}")
    print(f"   Confidence: {result['confidence']:.2f}")
    print(f"   Has Knowledge: {result['knowledge_response']['has_knowledge']}")
    
    if result['knowledge_response']['has_knowledge']:
        print(f"\n💬 Knowledge Response:")
        print(f"   {result['knowledge_response']['response']}")
    else:
        print(f"\n⚠️ No Knowledge Available:")
        print(f"   {result['knowledge_response']['response']}")
    
    print(f"\n✅ Domain Expert Agent working!")
    
    return result

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_domain_expert())