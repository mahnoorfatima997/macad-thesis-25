# orchestration/langgraph_orchestrator.py
from typing import Dict, Any, List, Literal
from langgraph.graph import StateGraph, END
from typing_extensions import TypedDict
import asyncio


# Import your agents
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from state_manager import ArchMentorState
from agents.analysis_agent import AnalysisAgent
from agents.socratic_tutor import SocraticTutorAgent
from agents.domain_expert import DomainExpertAgent
from agents.cognitive_enhancement import CognitiveEnhancementAgent

class WorkflowState(TypedDict):
    """LangGraph state that flows between agents"""
    # Core state
    student_state: ArchMentorState
    last_message: str
    
    # Context analysis
    student_classification: Dict[str, Any]
    routing_decision: Dict[str, Any]
    
    # Agent results
    analysis_result: Dict[str, Any]
    domain_expert_result: Dict[str, Any]
    socratic_result: Dict[str, Any]
    cognitive_enhancement_result: Dict[str, Any]  # ← ADD THIS LINE IF MISSING
    
    # Final output
    final_response: str
    response_metadata: Dict[str, Any]

class LangGraphOrchestrator:
    def __init__(self, domain="architecture"):
        self.domain = domain
        
        # Initialize agents
        self.analysis_agent = AnalysisAgent(domain)
        self.socratic_agent = SocraticTutorAgent(domain)
        self.domain_expert = DomainExpertAgent(domain)
        self.cognitive_enhancement_agent = CognitiveEnhancementAgent(domain)
        
        # Build the workflow graph
        self.workflow = self.build_workflow()
        
        print(f"🔄 LangGraph orchestrator initialized for {domain}")
    
    def build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow implementing your document's logic"""
        
        # Create the state graph
        workflow = StateGraph(WorkflowState)
        
        # Add nodes (agents and logic components)
        workflow.add_node("context_agent", self.context_agent_node)
        workflow.add_node("router", self.router_node)
        workflow.add_node("analysis_agent", self.analysis_agent_node)
        workflow.add_node("domain_expert", self.domain_expert_node)
        workflow.add_node("socratic_tutor", self.socratic_tutor_node)
        workflow.add_node("cognitive_enhancement", self.cognitive_enhancement_node)
        workflow.add_node("synthesizer", self.synthesizer_node)
        
        # Define the workflow edges (your document's decision tree)
        workflow.set_entry_point("context_agent")
        
        # Context Agent always goes to Router
        workflow.add_edge("context_agent", "router")
        
        # Router has conditional branches based on classification
        workflow.add_conditional_edges(
            "router",
            self.route_decision,
            {
                "knowledge_only": "domain_expert",
                "socratic_focus": "analysis_agent",
                "cognitive_challenge": "analysis_agent", 
                "multi_agent": "analysis_agent",
                "default": "analysis_agent"
            }
        )
        
        # Analysis always runs first for multi-agent paths
        workflow.add_conditional_edges(
            "analysis_agent",
            self.after_analysis_routing,
            {
                "to_domain_expert": "domain_expert",
                "to_socratic": "socratic_tutor",
                "to_cognitive": "cognitive_enhancement",  # ← ADD THIS LINE
                "to_synthesizer": "synthesizer"
            }
        )
        
        # Domain expert can go to socratic or synthesizer
        workflow.add_conditional_edges(
            "domain_expert",
            self.after_domain_expert,
            {
                "to_socratic": "socratic_tutor",
                "to_synthesizer": "synthesizer"
            }
        )
        
        # Socratic always goes to synthesizer
        workflow.add_edge("socratic_tutor", "synthesizer")
        
        # Cognitive enhancement agent goes to synthesizer
        workflow.add_edge("cognitive_enhancement", "synthesizer")
        # Synthesizer is the end
        workflow.add_edge("synthesizer", END)
        
        
        return workflow.compile()
    
    # NODE IMPLEMENTATIONS
    
    async def context_agent_node(self, state: WorkflowState) -> WorkflowState:
        """ENTRY POINT: Context Agent (Section 2 from your document)"""
        
        print("🔍 Context Agent: Analyzing student input...")
        
        student_state = state["student_state"]
        
        # Get last user message
        last_message = ""
        for msg in reversed(student_state.messages):
            if msg.get('role') == 'user':
                last_message = msg['content']
                break
        
        # Implement your document's context analysis logic
        classification = self.classify_student_input(last_message, student_state)
        
        return {
            **state,
            "last_message": last_message,
            "student_classification": classification
        }
    
    async def router_node(self, state: WorkflowState) -> WorkflowState:
        """ROUTER: Analyzes context and determines path (Section 3)"""
        
        print("🎯 Router: Determining agent path...")
        
        classification = state["student_classification"]
        routing_decision = self.determine_routing(classification)
        
        print(f"   Route chosen: {routing_decision['path']}")
        
        return {
            **state,
            "routing_decision": routing_decision
        }
    
    async def analysis_agent_node(self, state: WorkflowState) -> WorkflowState:
        """Analysis Agent: Always runs for multi-agent paths"""
        
        print("📊 Analysis Agent: Processing...")
        
        student_state = state["student_state"]
        analysis_result = await self.analysis_agent.process(student_state)
        
        return {
            **state,
            "analysis_result": analysis_result
        }
    
    async def domain_expert_node(self, state: WorkflowState) -> WorkflowState:
        """Domain Expert: Knowledge synthesis (Section 4)"""
        
        print("📚 Domain Expert: Providing knowledge...")
        
        student_state = state["student_state"]
        analysis_result = state.get("analysis_result", {})
        
        # Determine what knowledge gap to address
        cognitive_flags = analysis_result.get('cognitive_flags', [])
        if cognitive_flags:
            primary_gap = cognitive_flags[0].replace('needs_', '').replace('_guidance', '_awareness')
        else:
            primary_gap = "brief_development"
        
        domain_result = await self.domain_expert.provide_knowledge(
            student_state, analysis_result, primary_gap
        )
        
        return {
            **state,
            "domain_expert_result": domain_result
        }
    
    async def socratic_tutor_node(self, state: WorkflowState) -> WorkflowState:
        """Socratic Tutor: Question generation (Section 5)"""
        
        print("🤔 Socratic Tutor: Generating questions...")
        
        student_state = state["student_state"]
        analysis_result = state.get("analysis_result", {})
        
        socratic_result = await self.socratic_agent.generate_response(
            student_state, analysis_result
        )
        
        return {
            **state,
            "socratic_result": socratic_result
        }
    
    async def cognitive_enhancement_node(self, state: WorkflowState) -> WorkflowState:
        """Cognitive Enhancement Agent node - FIXED"""
        print("🧠 Cognitive Enhancement Agent: Enhancing cognition...")
        
        student_state = state["student_state"]
        analysis_result = state.get("analysis_result", {})
        
        # Get the classification from the state for context
        context_analysis = state.get("student_classification", {})
        
        enhancement_result = await self.cognitive_enhancement_agent.provide_challenge(
            student_state, context_analysis  # Use the correct context
        )
        
        print(f"🧠 DEBUG: Generated enhancement result: {enhancement_result}")  # Debug
        
        return {
            **state,
            "cognitive_enhancement_result": enhancement_result  # Store the result properly
        }
    
    async def synthesizer_node(self, state: WorkflowState) -> WorkflowState:
        """Synthesizer: Combines all agent outputs (Section 7)"""
        print("🔧 Synthesizer: Combining agent responses...")
        print("DEBUG cognitive_enhancement_result:", state.get("cognitive_enhancement_result"))
        final_response, metadata = self.synthesize_responses(state)
        return {
            **state,
            "final_response": final_response,
            "response_metadata": metadata
        }
    
    # ROUTING LOGIC
    
    def route_decision(self, state: WorkflowState) -> Literal["knowledge_only", "socratic_focus", "cognitive_challenge", "multi_agent", "default"]:
        """Router decision based on your document's logic"""
        
        routing = state["routing_decision"]
        return routing["path"]
    
    # In orchestration/langgraph_orchestrator.py - Fix after_analysis_routing method

    def after_analysis_routing(self, state: WorkflowState) -> Literal["to_domain_expert", "to_socratic", "to_cognitive", "to_synthesizer"]:
        """Enhanced routing after analysis - FIXED"""
        
        routing = state["routing_decision"]
        path = routing["path"]
        
        print(f"      🎯 After analysis routing for path: {path}")
        
        if path == "cognitive_challenge":
            print(f"         → Going to cognitive agent")
            return "to_cognitive"  # Go directly to cognitive agent
        elif path in ["multi_agent", "default"]:
            print(f"         → Going to domain expert first")
            return "to_domain_expert"  # Start with domain expert
        elif path == "socratic_focus":
            print(f"         → Going to socratic tutor")
            return "to_socratic"
        else:
            print(f"         → Going to synthesizer")
            return "to_synthesizer"
    
    def after_domain_expert(self, state: WorkflowState) -> Literal["to_socratic", "to_synthesizer"]:
        """Decide if we need Socratic after domain expert"""
        
        routing = state["routing_decision"]
        domain_result = state.get("domain_expert_result", {})
        
        # If we have knowledge, add Socratic questioning
        if domain_result.get("knowledge_response", {}).get("has_knowledge", False):
            return "to_socratic"
        else:
            return "to_synthesizer"
    
    # HELPER METHODS
    
    # In orchestration/langgraph_orchestrator.py - Fix classify_student_input method

    def classify_student_input(self, message: str, student_state: ArchMentorState) -> Dict[str, Any]:
        """IMPROVED classification with better keyword detection"""
        
        if not message:
            return {"classification": "initial", "understanding": "unknown", "confidence": "medium", "engagement": "medium"}
        
        message_lower = message.lower()
        
        # IMPROVED KEYWORD DETECTION
        
        # Overconfidence indicators (for cognitive_challenge)
        overconfidence_words = ["obviously", "clearly", "definitely", "perfect", "best", "optimal", "ideal", "flawless"]
        overconfidence_score = sum(1 for word in overconfidence_words if word in message_lower)
        
        # Feedback request indicators (for multi_agent)
        feedback_patterns = [
            "review my", "feedback on", "thoughts on", "critique", "evaluate", 
            "what do you think", "how does this look", "check my design", "can you review",
            "analyze my plan", "analyze my design", "look at my", "thoughts about my"  # ADD THESE
        ]

        is_feedback_request = any(pattern in message_lower for pattern in feedback_patterns)
        
        # Technical question indicators (for knowledge_only)
        technical_patterns = [
            "what are the", "what is the", "requirements for", "ada requirements",
            "building codes", "standards for", "guidelines", "regulations"
        ]
        is_technical_question = any(pattern in message_lower for pattern in technical_patterns)
        
        # Confusion indicators (for socratic_focus)
        confusion_words = ["confused", "don't understand", "unclear", "help", "lost", "stuck"]
        confusion_score = sum(1 for word in confusion_words if word in message_lower)
        
        # CLASSIFICATION LOGIC
        
        # 1. Understanding Level
        technical_terms = ["accessibility", "circulation", "programming", "design", "community", "building"]
        tech_usage = sum(1 for term in technical_terms if term in message_lower)
        
        if tech_usage >= 2:
            understanding = "high"
        elif tech_usage >= 1:
            understanding = "medium"
        else:
            understanding = "low"
        
        # 2. Confidence Level - FIXED
        if overconfidence_score >= 1:  # Lower threshold
            confidence = "overconfident"
        elif any(word in message_lower for word in ["think", "maybe", "might"]):
            confidence = "confident"
        else:
            confidence = "uncertain"
        
        # 3. Engagement Level
        word_count = len(message.split())
        if word_count > 10:
            engagement = "high"
        elif word_count > 5:
            engagement = "medium"
        else:
            engagement = "low"
        
        # 4. Interaction Type - FIXED
        if is_feedback_request:
            interaction_type = "design_feedback_request"
        elif is_technical_question:
            interaction_type = "technical_question"
        elif "?" in message:
            interaction_type = "question"
        else:
            interaction_type = "statement"
        
        print(f"      🔍 Classification Debug:")
        print(f"         Overconfidence score: {overconfidence_score}")
        print(f"         Is feedback request: {is_feedback_request}")
        print(f"         Is technical question: {is_technical_question}")
        print(f"         Confidence level: {confidence}")
        
        return {
            "classification": interaction_type,
            "understanding_level": understanding,
            "confidence_level": confidence,
            "engagement_level": engagement,
            "confusion_score": confusion_score,
            "overconfidence_score": overconfidence_score,  # NEW
            "word_count": word_count,
            "technical_usage": tech_usage,
            "is_technical_question": is_technical_question,
            "is_feedback_request": is_feedback_request
        }

    # In orchestration/langgraph_orchestrator.py - Fix the determine_routing method

    def determine_routing(self, classification: Dict[str, Any]) -> Dict[str, Any]:
        """FIXED: Proper priority order for routing decisions"""
        
        understanding = classification["understanding_level"]
        confidence = classification["confidence_level"]
        engagement = classification["engagement_level"]
        interaction_type = classification["classification"]
        
        # PRIORITY-BASED ROUTING (order matters!):
        
        # PRIORITY 1: Design feedback requests (regardless of understanding level)
        if classification["is_feedback_request"] or interaction_type == "design_feedback_request":
            return {"path": "multi_agent", "reason": "Design feedback requested"}
        
        # PRIORITY 2: Technical questions with decent understanding
        if classification["is_technical_question"] and understanding in ["medium", "high"]:
            return {"path": "knowledge_only", "reason": "Technical question with sufficient understanding"}
        
        # PRIORITY 3: Overconfidence (challenge assumptions even if understanding is low)
        if confidence == "overconfident":
            return {"path": "cognitive_challenge", "reason": "Overconfident language detected"}
        
        # PRIORITY 4: Explicit confusion or very low understanding
        if classification["confusion_score"] > 0:
            return {"path": "socratic_focus", "reason": "Explicit confusion signals"}
        
        # PRIORITY 5: Low understanding (but no explicit confusion)
        if understanding == "low":
            return {"path": "socratic_focus", "reason": "Low understanding level"}
        
        # PRIORITY 6: Low engagement
        if engagement == "low":
            return {"path": "cognitive_challenge", "reason": "Low engagement detected"}
        
        # PRIORITY 7: Default for everything else
        return {"path": "default", "reason": "Standard balanced support"}




    # below is the old version of synthesize_responses method indented in the document
    def synthesize_responses(self, state: WorkflowState) -> tuple[str, Dict[str, Any]]:
        """Implement Section 7 exactly as documented"""
        
        socratic_result = state.get("socratic_result", {})
        domain_result = state.get("domain_expert_result", {})
        cognitive_result = state.get("cognitive_enhancement_result", {})
        routing = state.get("routing_decision", {})
        
        # PRIORITY ORDER from document:
        final_response = ""
        response_type = ""
        
        # 1. SOCRATIC AGENT RESPONSE (if asking questions) - HIGHEST PRIORITY
        if socratic_result and socratic_result.get("response_text"):
            final_response = socratic_result["response_text"]
            response_type = "socratic_primary"
            
            # WEAVE knowledge into Socratic response if available
            if domain_result and domain_result.get("knowledge_response", {}).get("has_knowledge"):
                knowledge = domain_result["knowledge_response"]["response"]
                final_response = f"From architectural principles: {knowledge}\n\n{final_response}"
                response_type = "knowledge_woven_socratic"
                
        # 2. COGNITIVE AGENT ENHANCEMENT (if providing challenges)
        elif cognitive_result and cognitive_result.get("response_text"):
            final_response = cognitive_result["response_text"]
            response_type = "cognitive_primary"
            
            # Integrate with Socratic if available
            if socratic_result and socratic_result.get("response_text"):
                final_response = f"{final_response}\n\n{socratic_result['response_text']}"
                response_type = "cognitive_integrated_socratic"
                
        # 3. KNOWLEDGE AGENT SYNTHESIS (if providing information)
        elif domain_result and domain_result.get("knowledge_response", {}).get("has_knowledge"):
            knowledge = domain_result["knowledge_response"]["response"]
            # ALWAYS end with open-ended question (per document)
            final_response = f"{knowledge}\n\nHow might you apply these principles to your specific design challenge?"
            response_type = "knowledge_with_question"
            
        # Fallback
        else:
            final_response = "Let's explore this together. What do you think about this aspect of your design?"
            response_type = "exploratory_fallback"
        
        # AVOID INFORMATION DUMPING (per document)
        if len(final_response.split()) > 150:
            # Truncate and add question
            final_response = final_response[:500] + "...\n\nWhat's your initial reaction to this approach?"
        
        return final_response, {"response_type": response_type, "routing_path": routing.get("path")}
    # def synthesize_responses(self, state: WorkflowState) -> tuple[str, Dict[str, Any]]:
    #     """Debug version to see what's going wrong"""
        
    #     print("🔧 DEBUG: All state keys:", list(state.keys()))
        
    #     socratic_result = state.get("socratic_result", {})
    #     domain_result = state.get("domain_expert_result", {})
    #     cognitive_result = state.get("cognitive_enhancement_result", {})
    #     routing = state.get("routing_decision", {})
        
    #     print("🔧 DEBUG: Socratic result exists:", bool(socratic_result))
    #     print("🔧 DEBUG: Domain result exists:", bool(domain_result))
    #     print("🔧 DEBUG: Cognitive result exists:", bool(cognitive_result))
    #     print("🔧 DEBUG: Cognitive result content:", cognitive_result)
        
    #     final_response = ""
    #     response_type = ""
    #     sources = []
        
    # # For multi_agent path: Combine knowledge + socratic
    #     if routing.get("path") == "multi_agent":
    #         knowledge_text = ""
    #         if domain_result and domain_result.get("knowledge_response", {}).get("has_knowledge"):
    #             knowledge_text = domain_result["knowledge_response"]["response"]
            
    #         socratic_text = ""
    #         if socratic_result and socratic_result.get("response_text"):
    #             socratic_text = socratic_result["response_text"]
            
    #         # WEAVE THEM TOGETHER as per your document
    #         if knowledge_text and socratic_text:
    #             final_response = f"{knowledge_text}\n\n{socratic_text}"
    #         elif knowledge_text:
    #             final_response = f"{knowledge_text}\n\nHow might you apply this to your design?"
    #         else:
    #             final_response = socratic_text
        
    #     # For other paths: Use primary agent output
    #     elif routing.get("path") == "cognitive_challenge":
    #         final_response = cognitive_result.get("response_text", "")
    #     elif routing.get("path") == "socratic_focus":
    #         final_response = socratic_result.get("response_text", "")
    #     elif routing.get("path") == "knowledge_only":
    #         if domain_result and domain_result.get("knowledge_response", {}).get("has_knowledge"):
    #             knowledge_text = domain_result["knowledge_response"]["response"]
    #             final_response = f"{knowledge_text}\n\nWhat questions does this raise for your design?"
        
    #     # Keep all routing information
    #     return final_response, {
    #         "routing_path": routing.get("path"),  # PRESERVE routing decision
    #         "agents_used": [k for k in state.keys() if k.endswith("_result") and state[k]],
    #         "synthesis_method": "document_compliant"
    #     }

        
        # # Check cognitive response first for cognitive_challenge path
        # if cognitive_result and cognitive_result.get("response_text"):
        #     print("🔧 DEBUG: Using cognitive response")
        #     final_response = cognitive_result["response_text"]
        #     response_type = "cognitive_primary"
        # elif socratic_result and socratic_result.get("response_text"):
        #     print("🔧 DEBUG: Using socratic response")
        #     final_response = socratic_result["response_text"]
        #     response_type = "socratic_primary"
        # else:
        #     print("🔧 DEBUG: No valid response found - using fallback")
        #     final_response = "That's an interesting point. Can you tell me more about your thinking process?"
        #     response_type = "fallback"
        
        # print(f"🔧 DEBUG: Final response: {final_response[:50]}...")
        # print(f"🔧 DEBUG: Response type: {response_type}")
        
        # metadata = {
        #     "response_type": response_type,
        #     "sources": sources,
        #     "routing_path": routing.get("path", "unknown"),
        #     "agents_used": [k for k in ["socratic_result", "domain_expert_result", "cognitive_enhancement_result"] if state.get(k)],
        #     "reasoning": routing.get("reason", "")
        # }
        
        # return final_response, metadata
        
    # MAIN EXECUTION METHOD
    
    async def process_student_input(self, student_state: ArchMentorState) -> Dict[str, Any]:
        """Main method to process student input through the full workflow"""
        
        print("🚀 LangGraph Orchestrator: Starting workflow...")
        
        # Initialize workflow state
        initial_state = WorkflowState(
            student_state=student_state,
            last_message="",
            student_classification={},
            routing_decision={},
            analysis_result={},
            domain_expert_result={},
            socratic_result={},
            final_response="",
            response_metadata={}
        )
        
        # Execute the workflow
        final_state = await self.workflow.ainvoke(initial_state)
        
        print("✅ LangGraph workflow completed!")
        
        return {
            "response": final_state["final_response"],
            "metadata": final_state["response_metadata"],
            "routing_path": final_state["routing_decision"].get("path", "unknown"),
            "classification": final_state["student_classification"]
        }

# Test the LangGraph orchestrator
async def test_langgraph_orchestrator():
    print("🧪 Testing LangGraph Orchestrator...")
    
    orchestrator = LangGraphOrchestrator("architecture")
    
    # Test cases from your document's classification logic
    test_cases = [
        {
            "input": "What are the ADA requirements for door widths?",
            "expected_path": "knowledge_only"
        },
        {
            "input": "I'm really confused about accessibility",
            "expected_path": "socratic_focus"
        },
        {
            "input": "My design is obviously perfect",
            "expected_path": "cognitive_challenge"
        },
        {
            "input": "Can you review my community center design?",
            "expected_path": "multi_agent"
        }
    ]
    
    for i, test_case in enumerate(test_cases):
        print(f"\n📝 Test {i+1}: {test_case['input']}")
        
        # Create test state
        from state_manager import ArchMentorState, StudentProfile
        state = ArchMentorState()
        state.current_design_brief = "Design a community center for 200 people"
        state.student_profile = StudentProfile(skill_level="intermediate")
        state.messages.append({"role": "user", "content": test_case["input"]})
        
        # Process through LangGraph
        result = await orchestrator.process_student_input(state)
        
        print(f"   Expected Path: {test_case['expected_path']}")
        print(f"   Actual Path: {result['routing_path']}")
        print(f"   Response Type: {result['metadata'].get('response_type', 'N/A')}")
        print(f"   Response: {result['response'][:100]}...")

        
        # Check if routing matches expectation
        if result['routing_path'] == test_case['expected_path']:
            print("   ✅ Routing correct!")
        else:
            print("   ⚠️ Routing different than expected")

if __name__ == "__main__":
    asyncio.run(test_langgraph_orchestrator())