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
    cognitive_enhancement_result: Dict[str, Any] 
    
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
        """Enhanced context agent using the new ContextAgent"""
        
        from agents.context_agent import ContextAgent  # Import new agent
        
        if not hasattr(self, 'context_agent'):
            self.context_agent = ContextAgent(self.domain)
        
        student_state = state["student_state"]
        
        # Get last user message
        last_message = ""
        for msg in reversed(student_state.messages):
            if msg.get('role') == 'user':
                last_message = msg['content']
                break
        
        # Use new context agent for comprehensive analysis
        context_package = await self.context_agent.analyze_student_input(student_state, last_message)
        
        return {
            **state,
            "last_message": last_message,
            "student_classification": context_package["core_classification"],
            "context_metadata": context_package["contextual_metadata"],
            "conversation_patterns": context_package["conversation_patterns"],
            "routing_suggestions": context_package["routing_suggestions"],
            "agent_contexts": context_package["agent_contexts"]
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
        """Domain Expert: Knowledge synthesis - NO HARD-CODED TOPICS"""
        
        print("📚 Domain Expert: Providing knowledge...")
        
        student_state = state["student_state"]
        analysis_result = state.get("analysis_result", {})
        
        # Use cognitive flags from analysis, not hard-coded keywords
        cognitive_flags = analysis_result.get('cognitive_flags', [])
        if cognitive_flags:
            primary_gap = cognitive_flags[0].replace('needs_', '').replace('_guidance', '_awareness')
            print(f"🎯 Using primary cognitive flag: {primary_gap}")
        else:
            primary_gap = "brief_development"
            print(f"🎯 Using default: brief development")
        
        domain_result = await self.domain_expert.provide_knowledge(
            student_state, analysis_result, primary_gap
        )
        
        return {
            **state,
            "domain_expert_result": domain_result
        }
    
    async def socratic_tutor_node(self, state: WorkflowState) -> WorkflowState:
        """Socratic Tutor: Question generation - LISTEN TO USER INPUT"""
        
        print("🤔 Socratic Tutor: Generating questions...")
        
        student_state = state["student_state"]
        analysis_result = state.get("analysis_result", {})
        last_message = state.get("last_message", "").lower()
        
        # CHECK IF USER MADE A SPECIFIC CHOICE
        user_topic = None
        if "versatility" in last_message or "activities" in last_message:
            user_topic = "activity_versatility"
            print(f"🎯 User chose topic: activity versatility")
        elif "comfort" in last_message and "space" in last_message:
            user_topic = "space_comfort"
            print(f"🎯 User chose topic: space comfort")
        elif "central" in last_message and "space" in last_message:
            user_topic = "central_space_design"
            print(f"🎯 User chose topic: central space design")
        
        # Generate response based on USER'S ACTUAL CHOICE
        if user_topic:
            socratic_result = await self.generate_topic_specific_response(user_topic, student_state, analysis_result)
        else:
            # Fallback to normal socratic response
            socratic_result = await self.socratic_agent.generate_response(
                student_state, analysis_result
            )
        
        return {
            **state,
            "socratic_result": socratic_result
        }

    async def generate_topic_specific_response(self, user_topic: str, student_state: ArchMentorState, analysis_result: Dict) -> Dict[str, Any]:
        """Generate Socratic response about user's chosen topic"""
        
        # Create questions about what they ACTUALLY want to explore
        topic_questions = {
            "activity_versatility": [
                "What types of activities do you envision happening simultaneously in this central space?",
                "How might the space need to transform between different activities like meetings versus exhibitions?",
                "What furniture or elements would need to be flexible to support various activities?",
                "How could the space accommodate both intimate meetings and larger gatherings?"
            ],
            "space_comfort": [
                "What makes a space feel comfortable for different user groups?",
                "How might acoustic comfort differ between meeting and exhibition activities?",
                "What environmental factors affect comfort during long meetings versus brief gatherings?",
                "How could the space adapt to seasonal comfort needs in Copenhagen?"
            ],
            "central_space_design": [
                "How do you envision people moving through and using this central area?",
                "What relationship should the central space have with surrounding areas?",
                "How could the central space serve as both a destination and a transition zone?",
                "What would make this central area feel welcoming for community members?"
            ]
        }
        
        import random
        question = random.choice(topic_questions.get(user_topic, ["What specific aspect of this interests you most?"]))
        
        return {
            "agent": "socratic_tutor",
            "response_text": question,
            "response_type": "user_topic_focused",
            "primary_gap_addressed": user_topic,
            "educational_intent": f"Guide exploration of {user_topic.replace('_', ' ')}"
        }
    
    async def cognitive_enhancement_node(self, state: WorkflowState) -> WorkflowState:
        """Cognitive Enhancement Agent node - FIXED"""
        print("🧠 Cognitive Enhancement Agent: Enhancing cognition...")
        
        student_state = state["student_state"]
        analysis_result = state.get("analysis_result", {})
        context_classification = state.get("student_classification", {})
        routing_decision = state.get("routing_decision", {})
        
        # Use all 4 parameters as expected by the agent
        enhancement_result = await self.cognitive_enhancement_agent.provide_challenge(
            student_state, context_classification, analysis_result, routing_decision
        )
        
        print(f"🧠 DEBUG: Generated enhancement result: {enhancement_result}")
        
        return {
            **state,
            "cognitive_enhancement_result": enhancement_result
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
        
        routing = state.get("routing_decision", {})
        path = routing.get("path", "default")
        
        print(f"      🎯 After analysis routing for path: {path}")
        
        if path == "cognitive_challenge":
            print(f"         → Going to cognitive agent")
            return "to_cognitive"
        elif path == "socratic_focus":
            print(f"         → Going to socratic tutor")
            return "to_socratic"
        elif path in ["multi_agent", "default"]:
            print(f"         → Going to domain expert first")
            return "to_domain_expert"
        else:
            print(f"         → Going to synthesizer")
            return "to_synthesizer"
    
    def after_domain_expert(self, state: WorkflowState) -> Literal["to_socratic", "to_synthesizer"]:
        """Route after domain expert based on path"""
        
        routing = state.get("routing_decision", {})
        path = routing.get("path", "default")
        
        print(f"   🎯 After domain expert routing for path: {path}")
        
        if path == "knowledge_only":
            print("      → Going directly to synthesizer")
            return "to_synthesizer"
        elif path in ["multi_agent", "default"]:
            print("      → Going to socratic for sequence")
            return "to_socratic"
        else:
            print("      → Going to synthesizer")
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
            "analyze my plan", "analyze my design", "look at my", "thoughts about my",
            "how can i improve", "can you help me improve", "improve the", "improve my"
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

    #  determine_routing method

    def determine_routing(self, classification: Dict[str, Any]) -> Dict[str, Any]:
        """Dynamic routing based on AI classification - no hard-coding"""
        
        # Get AI-detected learning state
        confidence_level = classification.get("confidence_level", "confident")
        understanding_level = classification.get("understanding_level", "medium")
        engagement_level = classification.get("engagement_level", "medium")
        interaction_type = classification.get("interaction_type", "general_statement")
        is_technical = classification.get("is_technical_question", False)
        is_feedback_request = classification.get("is_feedback_request", False)
        shows_confusion = classification.get("shows_confusion", False)
        demonstrates_overconfidence = classification.get("demonstrates_overconfidence", False)
        
        print(f"📊 AI Classification: {confidence_level} confidence, {understanding_level} understanding, {engagement_level} engagement")
        
        # EXACT ROUTING LOGIC FROM YOUR DOCUMENT (Section 2)
        
        # IF student asks factual question + shows high understanding → Knowledge Agent only
        if is_technical and understanding_level == "high":
            routing_decision = {
                "path": "knowledge_only",
                "agents_to_activate": ["domain_expert"],
                "reason": "Technical question + high understanding",
                "confidence": 0.9
            }
        
        # IF student expresses confusion OR shows low understanding → Socratic Agent (primary) + Cognitive Agent (support)
        elif shows_confusion or understanding_level == "low":
            routing_decision = {
                "path": "socratic_focus",
                "agents_to_activate": ["socratic_tutor", "cognitive_enhancement"],
                "primary_agent": "socratic_tutor",
                "support_agent": "cognitive_enhancement",
                "reason": "Confusion or low understanding detected",
                "confidence": 0.8
            }
    # IF student shows overconfidence OR low engagement → Cognitive Agent (primary) + Socratic Agent (follow-up)
        elif demonstrates_overconfidence or engagement_level == "low":
            routing_decision = {
                "path": "cognitive_challenge",
                "agents_to_activate": ["cognitive_enhancement", "socratic_tutor"],
                "primary_agent": "cognitive_enhancement",
                "followup_agent": "socratic_tutor",
                "reason": f"Overconfidence: {demonstrates_overconfidence}, Low engagement: {engagement_level == 'low'}",
                "confidence": 0.9
            }
        
        # IF student requests design feedback → All agents (Knowledge → Socratic → Cognitive)
        elif is_feedback_request:
            routing_decision = {
                "path": "multi_agent",
                "agents_to_activate": ["domain_expert", "socratic_tutor", "cognitive_enhancement"],
                "sequence": ["domain_expert", "socratic_tutor", "cognitive_enhancement"],
                "reason": "Design feedback request - comprehensive response needed",
                "confidence": 0.8
            }
        
        # DEFAULT: Knowledge Agent + Socratic Agent (from your document)
        else:
            routing_decision = {
                "path": "default",
                "agents_to_activate": ["domain_expert", "socratic_tutor"],
                "reason": "Standard interaction - knowledge + guidance",
                "confidence": 0.6
            }
        
        print(f"✅ Route chosen: {routing_decision['path']}")
        print(f"🤖 Agents to activate: {routing_decision['agents_to_activate']}")
        
        return routing_decision




    #execution helper method
    async def execute_agent_sequence(self, state: WorkflowState) -> WorkflowState:
        """Execute agents based on routing decision"""
        
        routing = state.get("routing_decision", {})
        path = routing.get("path", "default")
        agents_to_activate = routing.get("agents_to_activate", [])
        
        print(f"🚀 Executing {path} path with agents: {agents_to_activate}")
        
        if path == "knowledge_only":
            # Only domain expert
            state = await self.domain_expert_node(state)
            
        elif path == "socratic_focus":
            # Socratic (primary) + Cognitive (support)
            state = await self.socratic_tutor_node(state)
            # Add cognitive support if needed
            if "cognitive_enhancement" in agents_to_activate:
                cognitive_state = await self.cognitive_enhancement_node(state)
                # Store as support, not primary
                state["cognitive_support_result"] = cognitive_state.get("cognitive_enhancement_result")
                
        elif path == "cognitive_challenge":
            # Cognitive (primary) + Socratic (follow-up)
            state = await self.cognitive_enhancement_node(state)
            # Add socratic follow-up
            if "socratic_tutor" in agents_to_activate:
                socratic_state = await self.socratic_tutor_node(state)
                state["socratic_followup_result"] = socratic_state.get("socratic_result")
                
        elif path == "multi_agent":
            # All agents in sequence: Knowledge → Socratic → Cognitive
            state = await self.domain_expert_node(state)
            state = await self.socratic_tutor_node(state)  
            state = await self.cognitive_enhancement_node(state)
            
        else:  # default
            # Knowledge + Socratic
            state = await self.domain_expert_node(state)
            state = await self.socratic_tutor_node(state)
        
        return state






    # response synthesis logic
    def synthesize_responses(self, state: WorkflowState) -> tuple[str, Dict[str, Any]]:
        """Implement priority: 1. Socratic 2. Cognitive 3. Knowledge"""
        
        routing = state.get("routing_decision", {})
        path = routing.get("path", "default")
        
        # Get agent results
        socratic_result = state.get("socratic_result", {})
        cognitive_result = state.get("cognitive_enhancement_result", {})
        domain_result = state.get("domain_expert_result", {})
        
        print(f"🔧 Synthesizing {path} path responses")
        
        # DOCUMENT PRIORITY ORDER: 1. Socratic 2. Cognitive 3. Knowledge
        final_response = ""
        response_type = ""
        sources = []
        
        if path == "socratic_focus":
            # Socratic primary + cognitive support
            final_response = socratic_result.get("response_text", "")
            response_type = "socratic_primary"
            
            # Add cognitive support insight if available
            cognitive_support = state.get("cognitive_support_result", {})
            if cognitive_support and cognitive_support.get("response_text"):
                final_response += f"\n\n{cognitive_support['response_text']}"
                response_type = "socratic_with_cognitive_support"
                
        elif path == "cognitive_challenge":
            # Cognitive primary + socratic follow-up
            final_response = cognitive_result.get("response_text", "")
            response_type = "cognitive_primary"
            
            # Add socratic follow-up if available
            socratic_followup = state.get("socratic_followup_result", {})
            if socratic_followup and socratic_followup.get("response_text"):
                final_response += f"\n\n{socratic_followup['response_text']}"
                response_type = "cognitive_with_socratic_followup"
                
        elif path == "knowledge_only":
            # Knowledge only
            knowledge_response = domain_result.get("knowledge_response", {})
            final_response = knowledge_response.get("response", "")
            response_type = "knowledge_only"
            sources = domain_result.get("sources", [])
            
        elif path == "multi_agent":
            # All agents: Follow priority order
            if socratic_result.get("response_text"):
                final_response = socratic_result["response_text"]
                response_type = "multi_agent_socratic_primary"
                
                # Weave in knowledge if available
                if domain_result.get("knowledge_response", {}).get("has_knowledge"):
                    knowledge = domain_result["knowledge_response"]["response"]
                    final_response = f"{knowledge}\n\n{final_response}"
                    response_type = "multi_agent_full"
                    sources = domain_result.get("sources", [])
            else:
                # Fallback to knowledge
                knowledge_response = domain_result.get("knowledge_response", {})
                final_response = knowledge_response.get("response", "")
                response_type = "multi_agent_knowledge_fallback"
                sources = domain_result.get("sources", [])
        
        else:  # default path
            # Knowledge + Socratic: Priority to Socratic
            if socratic_result.get("response_text"):
                final_response = socratic_result["response_text"]
                response_type = "default_socratic"
                
                # Weave knowledge if available
                if domain_result.get("knowledge_response", {}).get("has_knowledge"):
                    knowledge = domain_result["knowledge_response"]["response"]
                    final_response = f"{knowledge}\n\n{final_response}"
                    response_type = "default_knowledge_socratic"
                    sources = domain_result.get("sources", [])
            else:
                final_response = "Let's explore this together. What aspect would you like to focus on?"
                response_type = "fallback"
        
        if not final_response:
            final_response = "I'd like to help you explore this further. What specific aspect interests you most?"
            response_type = "safe_fallback"
        
        print(f"🔧 Final response type: {response_type}")
        
        metadata = {
            "response_type": response_type,
            "routing_path": path,
            "agents_used": routing.get("agents_to_activate", []),
            "sources": sources,
            "synthesis_method": "document_compliant"
        }
        
        return final_response, metadata
        
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