# orchestration/multi_agent_router.py
from typing import Dict, Any, List
from state_manager import ArchMentorState
from agents.analysis_agent import AnalysisAgent
from agents.socratic_tutor import SocraticTutorAgent
from agents.domain_expert import DomainExpertAgent
import re

class MultiAgentRouter:
    def __init__(self, domain="architecture"):
        self.domain = domain
        self.analysis_agent = AnalysisAgent(domain)
        self.socratic_agent = SocraticTutorAgent(domain)
        self.domain_expert = DomainExpertAgent(domain)
        
    async def process_student_input(self, state: ArchMentorState) -> Dict[str, Any]:
        """Main orchestration following your document's logic"""
        
        # 1. CONTEXT ANALYSIS (Entry Point)
        context_analysis = self.analyze_student_context(state)
        
        # 2. ROUTER DECISION (Based on your classification logic)
        routing_decision = self.route_agents(context_analysis)
        
        # 3. AGENT EXECUTION (Sequential/Parallel based on needs)
        agent_results = await self.execute_agents(routing_decision, state)
        
        # 4. RESPONSE SYNTHESIS (Combine outputs)
        final_response = self.synthesize_response(agent_results, context_analysis)
        
        return final_response
    
    def analyze_student_context(self, state: ArchMentorState) -> Dict[str, Any]:
        """Implements Section 2: Student Input Classification Logic"""
        
        # Get last user message
        last_message = ""
        for msg in reversed(state.messages):
            if msg.get('role') == 'user':
                last_message = msg['content']
                break
        
        if not last_message:
            return {"classification": "initial", "confidence": "unknown", "engagement": "medium"}
        
        # Parse emotional indicators
        confusion_indicators = ["confused", "don't understand", "unclear", "help", "lost"]
        confidence_indicators = ["I think", "obviously", "clearly", "definitely", "sure"]
        engagement_indicators = ["interesting", "exciting", "curious", "want to", "like to"]
        
        confusion_score = sum(1 for indicator in confusion_indicators if indicator in last_message.lower())
        confidence_score = sum(1 for indicator in confidence_indicators if indicator in last_message.lower())
        engagement_score = sum(1 for indicator in engagement_indicators if indicator in last_message.lower())
        
        # Analyze understanding level
        technical_terms = ["accessibility", "circulation", "programming", "spatial", "systems"]
        tech_usage = sum(1 for term in technical_terms if term in last_message.lower())
        
        # Response length analysis
        word_count = len(last_message.split())
        
        # Classification logic from your document
        understanding_level = "high" if tech_usage > 1 else "medium" if tech_usage > 0 else "low"
        confidence_level = "overconfident" if confidence_score > 1 else "confident" if confidence_score > 0 else "uncertain"
        engagement_level = "high" if engagement_score > 0 and word_count > 15 else "medium" if word_count > 5 else "low"
        
        # Interaction type
        if "?" in last_message:
            interaction_type = "question"
        elif any(word in last_message.lower() for word in ["feedback", "review", "thoughts", "opinion"]):
            interaction_type = "design_feedback_request"
        elif any(word in last_message.lower() for word in ["think", "believe", "consider"]):
            interaction_type = "reflection"
        else:
            interaction_type = "statement"
        
        return {
            "classification": interaction_type,
            "understanding_level": understanding_level,
            "confidence_level": confidence_level,
            "engagement_level": engagement_level,
            "confusion_score": confusion_score,
            "word_count": word_count,
            "message": last_message
        }
    
    def route_agents(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Implements Section 3: Agent Coordination Logic"""
        
        understanding = context["understanding_level"]
        confidence = context["confidence_level"]
        engagement = context["engagement_level"]
        interaction_type = context["classification"]
        
        # Routing logic from your document
        if interaction_type == "question" and understanding == "high":
            # IF student asks factual question + shows high understanding → ROUTE TO: Knowledge Agent only
            return {
                "primary_path": "knowledge_only",
                "agents": ["domain_expert"],
                "priority": "knowledge_synthesis"
            }
        
        elif understanding == "low" or context["confusion_score"] > 0:
            # IF student expresses confusion OR shows low understanding → ROUTE TO: Socratic Agent (primary) + Cognitive Agent (support)
            return {
                "primary_path": "socratic_focus",
                "agents": ["socratic_tutor"],
                "priority": "guided_discovery"
            }
        
        elif confidence == "overconfident" or engagement == "low":
            # IF student shows overconfidence OR low engagement → ROUTE TO: Cognitive Agent (primary) + Socratic Agent (follow-up)
            return {
                "primary_path": "cognitive_challenge",
                "agents": ["socratic_tutor"],  # We don't have cognitive agent yet
                "priority": "challenge_assumptions"
            }
        
        elif interaction_type == "design_feedback_request":
            # IF student requests design feedback → ROUTE TO: All agents (Knowledge → Socratic → Cognitive)
            return {
                "primary_path": "multi_agent",
                "agents": ["analysis", "domain_expert", "socratic_tutor"],
                "priority": "comprehensive_feedback"
            }
        
        else:
            # DEFAULT: Knowledge Agent + Socratic Agent
            return {
                "primary_path": "default",
                "agents": ["domain_expert", "socratic_tutor"],
                "priority": "balanced_support"
            }
    
    async def execute_agents(self, routing: Dict[str, Any], state: ArchMentorState) -> Dict[str, Any]:
        """Execute agents based on routing decision"""
        
        results = {}
        
        # Always run analysis first
        analysis_result = await self.analysis_agent.process(state)
        results["analysis"] = analysis_result
        
        # Execute based on routing
        if "domain_expert" in routing["agents"]:
            cognitive_flags = analysis_result.get('cognitive_flags', [])
            if cognitive_flags:
                primary_gap = cognitive_flags[0].replace('needs_', '').replace('_guidance', '_awareness')
                domain_result = await self.domain_expert.provide_knowledge(state, analysis_result, primary_gap)
                results["domain_expert"] = domain_result
        
        if "socratic_tutor" in routing["agents"]:
            socratic_result = await self.socratic_agent.generate_response(state, analysis_result)
            results["socratic_tutor"] = socratic_result
        
        return results
    
    def synthesize_response(self, agent_results: Dict, context: Dict) -> Dict[str, Any]:
        """Implements Section 7: Response Synthesis Logic"""
        
        # Priority order from your document:
        # 1. Socratic Agent response (if asking questions)
        # 2. Cognitive Agent enhancement (if providing challenges)  
        # 3. Knowledge Agent synthesis (if providing information)
        
        final_response = ""
        response_type = "combined"
        sources = []
        
        # Check for Socratic response first
        if "socratic_tutor" in agent_results:
            socratic = agent_results["socratic_tutor"]
            final_response = socratic["response_text"]
            response_type = "socratic_primary"
        
        # Add knowledge if available and relevant
        if "domain_expert" in agent_results:
            domain = agent_results["domain_expert"]
            if domain["knowledge_response"]["has_knowledge"]:
                if response_type == "socratic_primary":
                    # Weave knowledge into Socratic response
                    knowledge_part = domain["knowledge_response"]["response"]
                    final_response = f"{knowledge_part}\n\n{final_response}"
                    response_type = "knowledge_enhanced_socratic"
                else:
                    final_response = domain["knowledge_response"]["response"]
                    response_type = "knowledge_primary"
                
                sources = domain["sources"]
        
        return {
            "response": final_response,
            "response_type": response_type,
            "sources": sources,
            "routing_used": context,
            "agent_results": agent_results
        }

# Test the complete orchestration
async def test_orchestration():
    from state_manager import ArchMentorState, StudentProfile
    
    router = MultiAgentRouter("architecture")
    
    # Test different input types
    test_cases = [
        "I'm confused about accessibility requirements",  # Should route to Socratic
        "What are the building codes for community centers?",  # Should route to Knowledge
        "I think my design is perfect as is",  # Should route to Cognitive challenge
        "Can you review my design?",  # Should route to Multi-agent
    ]
    
    for test_input in test_cases:
        print(f"\n🧪 Testing: '{test_input}'")
        
        state = ArchMentorState()
        state.current_design_brief = "Design a community center"
        state.messages.append({"role": "user", "content": test_input})
        
        result = await router.process_student_input(state)
        
        print(f"   Response Type: {result['response_type']}")
        print(f"   Sources: {result['sources']}")
        print(f"   Response: {result['response'][:100]}...")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_orchestration())