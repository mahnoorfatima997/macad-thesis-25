# orchestration/langgraph_orchestrator.py
from typing import Dict, Any, List, Literal, Optional
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
from state_manager import*

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
        
        # Socratic tutor can go to cognitive enhancement or synthesizer
        workflow.add_conditional_edges(
            "socratic_tutor",
            self.after_socratic_tutor,
            {
                "to_cognitive": "cognitive_enhancement",
                "to_synthesizer": "synthesizer"
            }
        )
        
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
        
        print(f"🔍 Context Agent: Processing state with {len(student_state.messages)} messages")
        print(f"🔍 Context Agent: Messages: {[msg.get('role', 'unknown') for msg in student_state.messages]}")
        
        # Get last user message
        last_message = ""
        for msg in reversed(student_state.messages):
            if msg.get('role') == 'user':
                last_message = msg['content']
                break
        
        print(f"🔍 Context Agent: Last user message: {last_message[:50]}...")
        
        # Use new context agent for comprehensive analysis
        context_package = await self.context_agent.analyze_student_input(student_state, last_message)
        
        return {
            **state,
            "last_message": last_message,
            "student_classification": {**context_package["core_classification"], "last_message": last_message},
            "context_metadata": context_package["contextual_metadata"],
            "conversation_patterns": context_package["conversation_patterns"],
            "routing_suggestions": context_package["routing_suggestions"],
            "agent_contexts": context_package["agent_contexts"],
            "context_package": context_package  # Store full package for agents
        }
    
    async def router_node(self, state: WorkflowState) -> WorkflowState:
        """ROUTER: Use context agent's routing suggestions for smart routing"""
        
        print("🎯 Router: Determining agent path...")
        
        # Use context agent's routing suggestions instead of hardcoded logic
        routing_suggestions = state.get("routing_suggestions", {})
        classification = state["student_classification"]
        
        # Smart routing: Use context agent suggestions with thread awareness fallback
        if routing_suggestions.get("confidence", 0) > 0.7:
            # High confidence from context agent - use its suggestions
            routing_decision = self.create_smart_routing_decision(routing_suggestions, classification)
        else:
            # Lower confidence - use existing logic as fallback
            routing_decision = await self.determine_routing(routing_suggestions, classification, state["student_state"])
        
        print(f"   Route chosen: {routing_decision['path']}")
        print(f"   Confidence: {routing_decision['confidence']:.2f}")
        
        return {
            **state,
            "routing_decision": routing_decision
        }
    
    async def analysis_agent_node(self, state: WorkflowState) -> WorkflowState:
        """Analysis Agent: Always runs for multi-agent paths"""
        
        print("📊 Analysis Agent: Processing...")
        
        student_state = state["student_state"]
        context_package = state.get("context_package", {})
        
        # Pass context package to analysis agent for better continuity
        analysis_result = await self.analysis_agent.process(student_state, context_package)
        
        return {
            **state,
            "analysis_result": analysis_result
        }
    
    async def domain_expert_node(self, state: WorkflowState) -> WorkflowState:
        """Domain Expert: Knowledge synthesis with visual awareness"""
        
        print("📚 Domain Expert: Providing knowledge...")
        
        student_state = state["student_state"]
        analysis_result = state.get("analysis_result", {})
        
        # ENHANCED: Pass visual analysis to domain expert for sketch-aware responses
        visual_analysis = analysis_result.get('visual_analysis', {})
        if visual_analysis and not visual_analysis.get('error'):
            print("🖼️ Domain Expert: Including visual analysis context")
            # Store visual insights in student state for agent access
            student_state.agent_context['visual_insights'] = {
                'design_strengths': visual_analysis.get('design_strengths', []),
                'improvement_opportunities': visual_analysis.get('improvement_opportunities', []),
                'identified_elements': visual_analysis.get('identified_elements', []),
                'has_visual_analysis': True
            }
        else:
            student_state.agent_context['visual_insights'] = {'has_visual_analysis': False}
        
        # Pass visual context to analysis result for better coordination
        if visual_analysis and not visual_analysis.get('error'):
            analysis_result['visual_context'] = {
                'has_visual': True,
                'elements': visual_analysis.get('identified_elements', []),
                'strengths': visual_analysis.get('design_strengths', []),
                'opportunities': visual_analysis.get('improvement_opportunities', [])
            }
        else:
            analysis_result['visual_context'] = {'has_visual': False}
        
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
        """Socratic Tutor: AI-powered question generation for ANY topic"""
        
        print("🤔 Socratic Tutor: Generating questions...")
        
        student_state = state["student_state"]
        analysis_result = state.get("analysis_result", {})
        context_classification = state.get("student_classification", {})
        
        # Use enhanced Socratic agent with context classification
        socratic_result = await self.socratic_agent.generate_response(
            student_state, analysis_result, context_classification
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
    
    def route_decision(self, state: WorkflowState) -> str:
        """Simplified routing that ensures comprehensive responses"""
        
        print("🎯 Making routing decision...")
        
        # For most queries, we want both domain knowledge and Socratic guidance
        # This ensures comprehensive responses that both inform and guide thinking
        
        print(f"✅ Route chosen: comprehensive_guidance")
        print(f"🤖 Will activate: domain_expert + socratic_tutor")
        
        # Return the path that leads to analysis (which will then call both agents)
        return "default"
    
    # In orchestration/langgraph_orchestrator.py - Fix after_analysis_routing method

    def after_analysis_routing(self, state: WorkflowState) -> str:
        """Simplified routing after analysis that ensures comprehensive responses"""
        
        print("🎯 After analysis routing...")
        
        # For comprehensive responses, we want domain expert, Socratic tutor, and cognitive enhancement
        # The workflow will execute them in sequence
        
        print("🚀 Will execute: domain_expert → socratic_tutor → cognitive_enhancement → synthesizer")
        return "to_domain_expert"
    
    def after_domain_expert(self, state: WorkflowState) -> Literal["to_socratic", "to_synthesizer"]:
        """Always go to Socratic tutor after domain expert for comprehensive responses"""
        
        print("🎯 After domain expert: Going to Socratic tutor...")
        return "to_socratic"
    
    def after_socratic_tutor(self, state: WorkflowState) -> Literal["to_cognitive", "to_synthesizer"]:
        """Always go to cognitive enhancement after Socratic tutor for comprehensive responses"""
        
        print("🎯 After Socratic tutor: Going to cognitive enhancement...")
        return "to_cognitive"
    
    # HELPER METHODS
    
    def create_smart_routing_decision(self, routing_suggestions: Dict[str, Any], classification: Dict[str, Any]) -> Dict[str, Any]:
        """Create routing decision using context agent's suggestions with thread awareness"""
        
        # Use context agent's primary route suggestion
        primary_route = routing_suggestions.get("primary_route", "default")
        confidence = routing_suggestions.get("confidence", 0.6)
        reasoning = routing_suggestions.get("reasoning", ["Standard interaction"])
        
        # Convert routing suggestions to our workflow format
        routing_decision = {
            "path": primary_route,
            "confidence": confidence,
            "reason": "; ".join(reasoning),
            "ai_powered": True
        }
        
        # Map routes to agents to activate
        route_to_agents = {
            "knowledge_only": ["domain_expert"],
            "socratic_focus": ["socratic_tutor"],
            "cognitive_challenge": ["cognitive_enhancement"],
            "multi_agent": ["domain_expert", "socratic_tutor", "cognitive_enhancement"],
            "default": ["domain_expert", "socratic_tutor"]
        }
        
        routing_decision["agents_to_activate"] = route_to_agents.get(primary_route, ["domain_expert", "socratic_tutor"])
        
        return routing_decision
        
    # In orchestration/langgraph_orchestrator.py - Fix classify_student_input method

    def classify_student_input(self, message: str, student_state: ArchMentorState) -> Dict[str, Any]:
        """IMPROVED classification with better keyword detection"""

        if not message:
            return {"classification": "initial", "understanding": "unknown", "confidence": "medium", "engagement": "medium"}

        message_lower = message.lower()


        # Enhanced overconfidence indicators (for cognitive_challenge)
        overconfidence_words = ["obviously", "clearly", "definitely", "perfect", "best", "optimal", "ideal", "flawless"]
        absolute_patterns = ["this is the", "this will", "my design is", "the solution is", "it's clear that"]
        
        overconfidence_score = sum(1 for word in overconfidence_words if word in message_lower)
        overconfidence_score += sum(1 for pattern in absolute_patterns if pattern in message_lower)

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

        # Example/precedent/project request indicators (NEW)
        example_patterns = [
            "example", "examples", "precedent", "precedents", "case study", "case studies",
            "project", "projects", "reference", "references"
        ]
        is_example_request = any(pattern in message_lower for pattern in example_patterns) and "?" in message_lower

        # Confusion indicators (for socratic_focus)
        confusion_words = ["confused", "don't understand", "unclear", "help", "lost", "stuck"]
        confusion_score = sum(1 for word in confusion_words if word in message_lower)

        # Socratic clarification indicators
        socratic_clarification_patterns = [
            "what do you mean", "can you explain", "why did you ask", "why are you asking", "what's the point of", "what is the point of"
        ]
        is_socratic_clarification = any(pattern in message_lower for pattern in socratic_clarification_patterns)

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

        # 4. Interaction Type - PATCHED
        if is_feedback_request:
            interaction_type = "design_feedback_request"
        elif is_example_request:
            interaction_type = "example_request"
        elif is_technical_question:
            interaction_type = "technical_question"
        elif confusion_score > 0:
            interaction_type = "confusion_expression"
        elif "?" in message:
            interaction_type = "question"
        else:
            interaction_type = "statement"

        print(f"      🔍 Classification Debug:")
        print(f"         Overconfidence score: {overconfidence_score}")
        print(f"         Is feedback request: {is_feedback_request}")
        print(f"         Is technical question: {is_technical_question}")
        print(f"         Is example request: {is_example_request}")
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
            "is_feedback_request": is_feedback_request,
            "is_example_request": is_example_request
        }

    #  determine_routing method

    # Fix for langgraph_orchestrator.py - Enhanced Routing  

    # REPLACE the determine_routing method (around line 600) with this enhanced version:
    # COMPLETE FIX for langgraph_orchestrator.py - determine_routing method
    # REPLACE the entire determine_routing method with this complete version:

    async def determine_routing(self, routing_suggestions: Dict[str, Any], classification: Dict[str, Any], state: ArchMentorState = None) -> Dict[str, Any]:
        """Enhanced routing with better Socratic integration for design guidance"""

        # FIRST: Check if this is a continuation of an ongoing conversation thread
        if state and len(state.messages) >= 2:
            thread_continuation = await self._check_conversation_thread(state, classification)
            if thread_continuation:
                print(f"🔗 Continuing conversation thread: {thread_continuation['reason']}")
                return thread_continuation

        # Get the actual user input for analysis
        last_message = classification.get("last_message", "")
        
        # --- PURE EXAMPLE/PROJECT REQUEST DETECTION (knowledge_only) ---
        pure_example_keywords = [
            "example", "examples", "project", "projects", "precedent", "precedents",
            "case study", "case studies", "show me", "can you give", "can you provide",
            "can you show", "real project", "built project", "actual project"
        ]
        
        # Check if it's ONLY asking for examples (no design guidance)
        is_pure_example_request = (
            any(keyword in last_message.lower() for keyword in pure_example_keywords) and
            not any(word in last_message.lower() for word in ["how can i", "how do i", "how to", "how might", "incorporate", "integrate", "implement", "apply"])
        )
        
        if is_pure_example_request:
            print(f"✅ PURE EXAMPLE REQUEST: '{last_message}' → knowledge_only")
            return {
                "path": "knowledge_only",
                "agents_to_activate": ["domain_expert"],
                "reason": "Pure example/project request without design guidance needed",
                "confidence": 0.95
            }
        
        # --- DESIGN DECISION REQUEST DETECTION (socratic_focus) ---
        design_decision_patterns = [
            "can you suggest", "should i have", "should i use", "which one", "which should",
            "what should i choose", "what would you recommend", "recommend", "suggest",
            "better to have", "is it better", "which is better", "which approach",
            "one or two", "single or multiple", "big or small", "central or distributed"
        ]
        
        is_design_decision_request = any(pattern in last_message.lower() for pattern in design_decision_patterns)
        
        if is_design_decision_request:
            print(f"🤔 DESIGN DECISION REQUEST: '{last_message}' → socratic_focus")
            return {
                "path": "socratic_focus",
                "agents_to_activate": ["socratic_tutor"],
                "reason": "Design decision question needs Socratic guidance to help student think through options",
                "confidence": 0.95
            }
        
        # --- DESIGN GUIDANCE REQUEST DETECTION (default = Knowledge + Socratic) ---
        design_guidance_patterns = [
            "how can i", "how do i", "how to", "how might", "how should",
            "what's the best way", "what are ways to", "approaches to",
            "incorporate", "integrate", "implement", "apply", "use",
            "design", "create", "make", "develop", "enhance", "improve"
        ]
        
        is_design_guidance_request = any(pattern in last_message.lower() for pattern in design_guidance_patterns)
        
        if is_design_guidance_request:
            print(f"🎯 DESIGN GUIDANCE REQUEST: '{last_message}' → default (Knowledge + Socratic)")
            return {
                "path": "default",
                "agents_to_activate": ["domain_expert", "socratic_tutor"],
                "reason": "Design guidance request needs both knowledge and Socratic questioning",
                "confidence": 0.9
            }
        
        # Get classification details for other routing decisions
        confidence_level = classification.get("confidence_level", "confident")
        understanding_level = classification.get("understanding_level", "medium")
        engagement_level = classification.get("engagement_level", "medium")
        interaction_type = classification.get("classification", "general_statement")
        is_technical = classification.get("is_technical_question", False)
        is_feedback_request = classification.get("is_feedback_request", False)
        shows_confusion = classification.get("shows_confusion", False)
        demonstrates_overconfidence = classification.get("demonstrates_overconfidence", False)
        is_knowledge_seeking = classification.get("interaction_type") == "knowledge_seeking"
        is_socratic_clarification = classification.get("is_socratic_clarification", False)

        print(f"📊 Classification: {confidence_level} confidence, {understanding_level} understanding, {engagement_level} engagement")
        print(f"📊 Interaction type: {classification.get('interaction_type', 'unknown')}")
    # CONTINUING the determine_routing method - PRESERVED ALL ORIGINAL LOGIC:

        # Handle socratic clarification requests
        if is_socratic_clarification:
            routing_decision = {
                "path": "socratic_explanation",
                "agents_to_activate": ["socratic_explainer"],
                "reason": "User asked for clarification about Socratic question",
                "confidence": 1.0
            }

        # 1. Technical questions (standards, codes, requirements) → knowledge_only
        elif is_technical:
            routing_decision = {
                "path": "knowledge_only", 
                "agents_to_activate": ["domain_expert"],
                "reason": "Technical question requiring specific knowledge",
                "confidence": 0.9
            }
        
        # 2. Design help/improvement requests need Socratic guidance
        elif (any(word in last_message.lower() for word in ["how can i", "how do i", "don't know how", "help me"]) or
            any(word in last_message.lower() for word in ["improve", "enhance", "better", "develop"]) or
            shows_confusion):
            routing_decision = {
                "path": "default",  # Knowledge + Socratic
                "agents_to_activate": ["domain_expert", "socratic_tutor"],
                "reason": "Design improvement/guidance request needs Socratic support",
                "confidence": 0.85
            }
        
        # 3. Pure knowledge seeking (what/definitions) goes to knowledge only
        elif (is_knowledge_seeking and 
            any(word in last_message.lower() for word in ["what are", "what is", "definition", "standard", "requirement"])):
            routing_decision = {
                "path": "knowledge_only",
                "agents_to_activate": ["domain_expert"], 
                "reason": "General knowledge/definition request",
                "confidence": 0.8
            }
        
        # 4. Confusion or low understanding → Socratic focus
        elif (shows_confusion or understanding_level == "low" or 
            confidence_level == "uncertain" or 
            classification.get("interaction_type") == "confusion_expression"):
            routing_decision = {
                "path": "socratic_focus",
                "agents_to_activate": ["socratic_tutor"],
                "reason": f"Confusion/low understanding: {shows_confusion}, {understanding_level}, {confidence_level}",
                "confidence": 0.85
            }
        
        # 5. Overconfidence or low engagement → Cognitive challenge
        elif demonstrates_overconfidence or engagement_level == "low":
            routing_decision = {
                "path": "cognitive_challenge",
                "agents_to_activate": ["cognitive_enhancement", "socratic_tutor"],
                "primary_agent": "cognitive_enhancement",
                "followup_agent": "socratic_tutor",
                "reason": f"Overconfidence: {demonstrates_overconfidence}, Low engagement: {engagement_level == 'low'}",
                "confidence": 0.9
            }
        
        # 6. Feedback requests → Multi-agent
        elif is_feedback_request:
            routing_decision = {
                "path": "multi_agent",
                "agents_to_activate": ["domain_expert", "socratic_tutor", "cognitive_enhancement"],
                "sequence": ["domain_expert", "socratic_tutor", "cognitive_enhancement"],
                "reason": "Design feedback request - comprehensive response needed",
                "confidence": 0.8
            }
        
        # 7. Default → Knowledge + Socratic for design thinking
        else:
            routing_decision = {
                "path": "default",
                "agents_to_activate": ["domain_expert", "socratic_tutor"],
                "reason": "Standard interaction - knowledge + Socratic guidance for design thinking",
                "confidence": 0.6
            }

        print(f"✅ Route chosen: {routing_decision['path']}")
        print(f"🤖 Agents to activate: {routing_decision['agents_to_activate']}")

        return routing_decision
    # ENHANCED ROUTING LOGIC - PRESERVING ALL ORIGINAL LOGIC
    # async def determine_routing(self, routing_suggestions: Dict[str, Any], classification: Dict[str, Any], state: ArchMentorState = None) -> Dict[str, Any]:
    #     """Fallback routing with conversation thread awareness and better example detection"""

    #     # FIRST: Check if this is a continuation of an ongoing conversation thread
    #     if state and len(state.messages) >= 2:
    #         thread_continuation = await self._check_conversation_thread(state, classification)
    #         if thread_continuation:
    #             print(f"🔗 Continuing conversation thread: {thread_continuation['reason']}")
    #             return thread_continuation

    #     # Get the actual user input for robust pattern matching
    #     last_message = classification.get("last_message", "")
        
    #     # --- ENHANCED EXAMPLE/PROJECT/PRECEDENT DETECTION ---
    #     example_keywords = [
    #         "example", "examples", "project", "projects", "precedent", "precedents",
    #         "case study", "case studies", "show me", "can you give", "can you provide",
    #         "can you show", "real project", "built project", "actual project",
    #         "reference", "references", "inspiration"
    #     ]
        
    #     # Use both AI classification AND keyword matching for robustness
    #     is_example_request = (
    #         classification.get("is_example_request", False) or
    #         classification.get("interaction_type") == "example_request" or
    #         any(keyword in last_message.lower() for keyword in example_keywords)
    #     )
        
    #     if is_example_request:
    #         print(f"✅ EXAMPLE REQUEST DETECTED: '{last_message}'")
    #         routing_decision = {
    #             "path": "knowledge_only",
    #             "agents_to_activate": ["domain_expert"],
    #             "reason": "User requested examples/projects/precedents",
    #             "confidence": 0.95
    #         }
    #         print(f"   → Routing to knowledge_only for examples")
    #         return routing_decision
        
    #     # Get AI-detected learning state for other routing decisions
    #     confidence_level = classification.get("confidence_level", "confident")
    #     understanding_level = classification.get("understanding_level", "medium")
    #     engagement_level = classification.get("engagement_level", "medium")
    #     interaction_type = classification.get("classification", "general_statement")
    #     is_technical = classification.get("is_technical_question", False)
    #     is_feedback_request = classification.get("is_feedback_request", False)
    #     shows_confusion = classification.get("shows_confusion", False)
    #     demonstrates_overconfidence = classification.get("demonstrates_overconfidence", False)
    #     is_knowledge_seeking = classification.get("interaction_type") == "knowledge_seeking"
        
    #     print(f"📊 Classification: {confidence_level} confidence, {understanding_level} understanding, {engagement_level} engagement")
    #     print(f"📊 Interaction type: {classification.get('interaction_type', 'unknown')}")

    #     # ROUTING LOGIC - FIXED ORDER
        
    #     # 1. Technical questions go to knowledge only
    #     if is_technical:
    #         routing_decision = {
    #             "path": "knowledge_only", 
    #             "agents_to_activate": ["domain_expert"],
    #             "reason": "Technical question requiring specific knowledge",
    #             "confidence": 0.9
    #         }
        
    #     # 2. Design help/improvement requests need Socratic guidance
    #     elif (any(word in last_message.lower() for word in ["how can i", "how do i", "don't know how", "help me"]) or
    #         any(word in last_message.lower() for word in ["improve", "enhance", "better", "develop"]) or
    #         shows_confusion):
    #         routing_decision = {
    #             "path": "default",  # Knowledge + Socratic
    #             "agents_to_activate": ["domain_expert", "socratic_tutor"],
    #             "reason": "Design improvement/guidance request needs Socratic support",
    #             "confidence": 0.85
    #         }
        
    #     # 3. Pure knowledge seeking (what/definitions) goes to knowledge only
    #     elif (is_knowledge_seeking and 
    #         any(word in last_message.lower() for word in ["what are", "what is", "definition", "standard", "requirement"])):
    #         routing_decision = {
    #             "path": "knowledge_only",
    #             "agents_to_activate": ["domain_expert"], 
    #             "reason": "General knowledge/definition request",
    #             "confidence": 0.8
    #         }
        
    #     # 4. Confusion or low understanding → Socratic focus
    #     elif (shows_confusion or understanding_level == "low" or 
    #         confidence_level == "uncertain" or 
    #         classification.get("interaction_type") == "confusion_expression"):
    #         routing_decision = {
    #             "path": "socratic_focus",
    #             "agents_to_activate": ["socratic_tutor"],
    #             "reason": f"Confusion/low understanding detected: {shows_confusion}, {understanding_level}, {confidence_level}",
    #             "confidence": 0.85
    #         }
        
    #     # 5. Overconfidence or low engagement → Cognitive challenge
    #     elif demonstrates_overconfidence or engagement_level == "low":
    #         routing_decision = {
    #             "path": "cognitive_challenge",
    #             "agents_to_activate": ["cognitive_enhancement", "socratic_tutor"],
    #             "primary_agent": "cognitive_enhancement",
    #             "followup_agent": "socratic_tutor",
    #             "reason": f"Overconfidence: {demonstrates_overconfidence}, Low engagement: {engagement_level == 'low'}",
    #             "confidence": 0.9
    #         }
        
    #     # 6. Feedback requests → Multi-agent
    #     elif is_feedback_request:
    #         routing_decision = {
    #             "path": "multi_agent",
    #             "agents_to_activate": ["domain_expert", "socratic_tutor", "cognitive_enhancement"],
    #             "sequence": ["domain_expert", "socratic_tutor", "cognitive_enhancement"],
    #             "reason": "Design feedback request - comprehensive response needed",
    #             "confidence": 0.8
    #         }
        
    #     # 7. Default → Knowledge + Socratic
    #     else:
    #         routing_decision = {
    #             "path": "default",
    #             "agents_to_activate": ["domain_expert", "socratic_tutor"],
    #             "reason": "Standard interaction - knowledge + guidance",
    #             "confidence": 0.6
    #         }

    #     print(f"✅ Route chosen: {routing_decision['path']}")
    #     print(f"🤖 Agents to activate: {routing_decision['agents_to_activate']}")

    #     return routing_decision

    # ALSO REPLACE the _check_conversation_thread method to improve follow-up detection:

    async def _check_conversation_thread(self, state: ArchMentorState, classification: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Enhanced conversation thread detection with better example follow-up detection"""

        if len(state.messages) < 2:
            return None

        # Get last assistant message and current user message
        last_assistant_msg = None
        current_user_msg = None

        for msg in reversed(state.messages):
            if msg.get('role') == 'assistant' and not last_assistant_msg:
                last_assistant_msg = msg.get('content', '')
            elif msg.get('role') == 'user' and not current_user_msg:
                current_user_msg = msg.get('content', '')

        if not last_assistant_msg or not current_user_msg:
            return None

        # --- ENHANCED FOLLOW-UP EXAMPLE REQUEST DETECTION ---
        followup_example_patterns = [
            "another example", "more examples", "different example", "other example",
            "another project", "more projects", "different project", "other projects", 
            "another precedent", "more precedents", "different precedent", "other precedents",
            "can you give another", "can you show another", "can you provide another",
            "give me another", "show me another", "any other", "what about another"
        ]
        
        if any(pattern in current_user_msg.lower() for pattern in followup_example_patterns):
            print("🔗 Detected follow-up example/project/precedent request")
            return {
                "path": "knowledge_only",
                "agents_to_activate": ["domain_expert"],
                "reason": "User requested additional examples/projects/precedents",
                "confidence": 0.97,
                "thread_type": "followup_example_request"
            }

        # Use AI to detect other conversation thread types
        try:
            from openai import OpenAI
            import os

            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

            thread_detection_prompt = f"""
            CONVERSATION ANALYSIS:
            System said: "{last_assistant_msg}"
            User replied: "{current_user_msg}"

            Is the user continuing the conversation thread? Analyze if the user is:
            1. Requesting more examples/references/projects/precedents
            2. Answering a question the system asked
            3. Showing interest and wanting to explore the same topic deeper
            4. Asking follow-up questions about the same topic

            Respond with ONLY:
            - "EXAMPLE_REQUEST" if requesting examples/projects/precedents
            - "ANSWER_CONTINUATION" if answering system's question
            - "TOPIC_CONTINUATION" if continuing same topic exploration
            - "SOCRATIC_CONTINUATION" if answering a Socratic question
            - "NEW_TOPIC" if starting something completely different
            """

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": thread_detection_prompt}],
                max_tokens=20,
                temperature=0.3
            )

            thread_type = response.choices[0].message.content.strip()

            print(f"🧠 AI Thread Detection: {thread_type}")

            # Route based on AI detection
            if thread_type == "EXAMPLE_REQUEST":
                return {
                    "path": "knowledge_only",
                    "agents_to_activate": ["domain_expert"],
                    "reason": "AI detected: User requesting examples/references",
                    "confidence": 0.95,
                    "thread_type": "ai_example_continuation"
                }
            elif thread_type == "ANSWER_CONTINUATION":
                return {
                    "path": "knowledge_only", 
                    "agents_to_activate": ["domain_expert"],
                    "reason": "AI detected: User answered system's question",
                    "confidence": 0.9,
                    "thread_type": "ai_answer_continuation"
                }
            elif thread_type == "TOPIC_CONTINUATION":
                return {
                    "path": "knowledge_only",
                    "agents_to_activate": ["domain_expert"], 
                    "reason": "AI detected: User continuing topic exploration",
                    "confidence": 0.85,
                    "thread_type": "ai_topic_continuation"
                }
            elif thread_type == "SOCRATIC_CONTINUATION":
                return {
                    "path": "socratic_focus",
                    "agents_to_activate": ["socratic_tutor"],
                    "reason": "AI detected: User answering Socratic question",
                    "confidence": 0.8,
                    "thread_type": "ai_socratic_continuation"
                }

            # If "NEW_TOPIC" or AI uncertain, continue with normal routing
            return None

        except Exception as e:
            print(f"⚠️ AI thread detection failed: {e}")
            return None

    async def _check_conversation_thread(self, state: ArchMentorState, classification: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """AI-powered conversation thread detection - no hardcoding"""

        if len(state.messages) < 2:
            return None

        # Get last assistant message and current user message
        last_assistant_msg = None
        current_user_msg = None

        for msg in reversed(state.messages):
            if msg.get('role') == 'assistant' and not last_assistant_msg:
                last_assistant_msg = msg.get('content', '')
            elif msg.get('role') == 'user' and not current_user_msg:
                current_user_msg = msg.get('content', '')

        if not last_assistant_msg or not current_user_msg:
            return None

        # --- PATCH: Robust pattern matching for follow-up example requests ---
        followup_patterns = [
            "another example", "more examples", "different example", "other example",
            "another project", "different project", "other project", "more project",
            "another precedent", "more precedent", "different precedent", "other precedent",
            "can you give another", "can you show another", "can you provide another"
        ]
        if any(p in current_user_msg.lower() for p in followup_patterns):
            print("🔗 Detected follow-up example/project/precedent request in conversation thread.")
            return {
                "path": "knowledge_only",
                "agents_to_activate": ["domain_expert"],
                "reason": "User requested another example/project/precedent",
                "confidence": 0.97,
                "thread_type": "manual_example_followup"
            }
        # --- END PATCH ---

        # Use AI to detect conversation thread continuation (existing code)
        try:
            from openai import OpenAI
            import os

            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

            thread_detection_prompt = f"""
            CONVERSATION ANALYSIS:
            System said: "{last_assistant_msg}"
            User replied: "{current_user_msg}"

            Is the user continuing the conversation thread? Analyze if the user is:
            1. Requesting more examples/references/projects/precedents (phrases like "another example", "can you give another", "more examples")
            2. Answering a question the system asked
            3. Showing interest and wanting to explore the same topic deeper
            4. Asking follow-up questions about the same topic

            CRITICAL: Look for continuation patterns:
            - "another example", "can you give another", "give another example"
            - "more examples", "additional examples", "other examples"
            - "what about", "any other", "different example"

            Respond with ONLY:
            - "EXAMPLE_REQUEST" if ONLY asking for examples with no substantial response
            - "SOCRATIC_WITH_EXAMPLE_REQUEST" if answering/responding to questions AND requesting examples
            - "ANSWER_CONTINUATION" if answering system's question without requesting examples
            - "TOPIC_CONTINUATION" if continuing same topic exploration
            - "SOCRATIC_CONTINUATION" if thoughtfully answering a Socratic question
            - "NEW_TOPIC" if starting something completely different
            """

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": thread_detection_prompt}],
                max_tokens=20,
                temperature=0.3
            )

            thread_type = response.choices[0].message.content.strip()

            print(f"🧠 AI Thread Detection: {thread_type}")
            print(f"🔍 User said: '{current_user_msg}'")
            print(f"🔍 System said: '{last_assistant_msg[:100]}...'")

            # --- PATCH: Override thread detection if overconfidence or low engagement/understanding ---
            overconfident = classification.get("confidence_level") == "overconfident"
            low_engagement = classification.get("engagement_level") == "low"
            low_understanding = classification.get("understanding_level") == "low"
            if overconfident or low_engagement or low_understanding:
                print("⚡ Overconfidence or low engagement/understanding detected in thread, routing to cognitive_challenge")
                return {
                    "path": "cognitive_challenge",
                    "agents_to_activate": ["cognitive_enhancement", "socratic_tutor"],
                    "primary_agent": "cognitive_enhancement",
                    "followup_agent": "socratic_tutor",
                    "reason": "Overconfidence or low engagement/understanding detected in thread",
                    "confidence": 0.95,
                    "thread_type": "override_cognitive_challenge"
                }
            # --- END PATCH ---

            # Route based on AI detection
            if thread_type == "EXAMPLE_REQUEST":
                return {
                    "path": "knowledge_only",
                    "agents_to_activate": ["domain_expert"],
                    "reason": "AI detected: User requesting examples/references",
                    "confidence": 0.95,
                    "thread_type": "ai_example_continuation"
                }
            elif thread_type == "SOCRATIC_WITH_EXAMPLE_REQUEST":
                return {
                    "path": "multi_agent",
                    "agents_to_activate": ["domain_expert", "socratic_tutor"],
                    "reason": "AI detected: User answered Socratic questions AND requested examples",
                    "confidence": 0.9,
                    "thread_type": "ai_socratic_with_examples"
                }
            elif thread_type == "ANSWER_CONTINUATION":
                return {
                    "path": "knowledge_only", 
                    "agents_to_activate": ["domain_expert"],
                    "reason": "AI detected: User answered system's question",
                    "confidence": 0.9,
                    "thread_type": "ai_answer_continuation"
                }
            elif thread_type == "TOPIC_CONTINUATION":
                return {
                    "path": "knowledge_only",
                    "agents_to_activate": ["domain_expert"], 
                    "reason": "AI detected: User continuing topic exploration",
                    "confidence": 0.85,
                    "thread_type": "ai_topic_continuation"
                }
            elif thread_type == "SOCRATIC_CONTINUATION":
                return {
                    "path": "socratic_focus",
                    "agents_to_activate": ["socratic_tutor"],
                    "reason": "AI detected: User answering Socratic question",
                    "confidence": 0.8,
                    "thread_type": "ai_socratic_continuation"
                }

            # If "NEW_TOPIC" or AI uncertain, continue with normal routing
            return None

        except Exception as e:
            print(f"⚠️ AI thread detection failed: {e}")
            return None




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
    # ALSO ENHANCE the synthesize_responses method for better Socratic integration:
    # REPLACE the existing synthesize_responses method with this enhanced version:

    def synthesize_responses(self, state: WorkflowState) -> tuple[str, Dict[str, Any]]:
        """Simple, effective response synthesis that combines domain knowledge with Socratic guidance"""
        
        print(f"🔧 Synthesizing responses...")
        
        # Get agent results
        socratic_result = state.get("socratic_result", {})
        domain_result = state.get("domain_expert_result", {})
        analysis_result = state.get("analysis_result", {})
        cognitive_result = state.get("cognitive_enhancement_result", {})
        classification = state.get("student_classification", {})
        
        print(f"🔧 Available results: socratic={bool(socratic_result)}, domain={bool(domain_result)}, cognitive={bool(cognitive_result)}")
        
        # Get user's original input
        user_input = state.get("last_message", "")
        
        # Create sophisticated response by combining domain knowledge with Socratic guidance
        if domain_result and socratic_result:
            # Both domain knowledge and Socratic guidance available
            domain_text = domain_result.get("response_text", "")
            socratic_text = socratic_result.get("response_text", "")
            
            final_response = f"{domain_text}\n\n{socratic_text}"
            response_type = "multi_agent_synthesis"
            print(f"🔧 Combining domain knowledge + Socratic guidance")
            
        elif domain_result:
            # Only domain knowledge available
            final_response = domain_result.get("response_text", "")
            response_type = "domain_knowledge"
            print(f"🔧 Using domain knowledge only")
            
        elif socratic_result:
            # Only Socratic guidance available
            socratic_text = socratic_result.get("response_text", "")
            final_response = socratic_text
            response_type = "socratic_guidance"
            print(f"🔧 Using Socratic guidance only")
            
        elif cognitive_result:
            # Only cognitive enhancement available
            cognitive_text = cognitive_result.get("response_text", "")
            final_response = cognitive_text
            response_type = "cognitive_enhancement"
            print(f"🔧 Using cognitive enhancement only")
            
        else:
            # Fallback response
            final_response = "I'd be happy to help you with your architectural project. What specific aspect would you like to explore?"
            response_type = "fallback"
            print(f"🔧 Using fallback response")
        
        # Remove automatic cognitive summary appending to eliminate repetitive text
        
        # Determine which agents were used
        agents_used = []
        if socratic_result:
            agents_used.append("socratic_tutor")
        if domain_result:
            agents_used.append("domain_expert")
        if analysis_result:
            agents_used.append("analysis_agent")
        if cognitive_result:
            agents_used.append("cognitive_enhancement")
        
        # Extract phase analysis from analysis result
        phase_analysis = analysis_result.get("phase_analysis", {}) if analysis_result else {}
        
        # Extract scientific metrics from cognitive result
        scientific_metrics = cognitive_result.get("scientific_metrics", {}) if cognitive_result else {}
        cognitive_state = cognitive_result.get("cognitive_state", {}) if cognitive_result else {}
        
        # Combine all metadata
        metadata = {
            "response_type": response_type,
            "agents_used": agents_used,
            "routing_path": state.get("routing_decision", {}).get("path", "unknown"),
            "phase_analysis": phase_analysis,
            "scientific_metrics": scientific_metrics,
            "cognitive_state": cognitive_state,
            "analysis_result": analysis_result,
            "sources": domain_result.get("sources", []) if domain_result else [],
            "response_time": 0,  # Could be calculated if needed
            "classification": classification
        }
        
        print(f"🔧 Final response type: {response_type}")
        print(f"🔧 Final response: {final_response[:100]}...")
        print(f"🔧 Agents used: {agents_used}")
        print(f"🔧 Phase detected: {phase_analysis.get('current_phase', 'unknown')} (confidence: {phase_analysis.get('confidence', 0):.2f})")
        
        return final_response, metadata
    
    def _synthesize_example_response(self, domain_result: Dict, user_input: str, classification: Dict) -> str:
        """Synthesize focused example response"""
        
        if domain_result and domain_result.get("response_text"):
            return domain_result["response_text"]
        
        # Fallback example response
        return f"I'd be happy to help you with examples! Could you tell me more specifically what you're looking for? This will help me provide the most relevant examples for your project."
    
    def _synthesize_feedback_response(self, socratic_result: Dict, domain_result: Dict, user_input: str, classification: Dict) -> str:
        """Synthesize focused feedback response"""
        
        if socratic_result and socratic_result.get("response_text"):
            return socratic_result["response_text"]
        
        if domain_result and domain_result.get("response_text"):
            return domain_result["response_text"]
        
        # Fallback feedback response
        return "I'd be glad to provide feedback on your design! To give you the most useful feedback, could you tell me what specific aspects of your project you'd like me to focus on?"
    
    def _synthesize_technical_response(self, domain_result: Dict, user_input: str, classification: Dict) -> str:
        """Synthesize focused technical response"""
        
        if domain_result and domain_result.get("response_text"):
            return domain_result["response_text"]
        
        # Fallback technical response
        return "I'd be happy to help with technical requirements! Could you specify what technical aspects you need information about?"
    
    def _synthesize_clarification_response(self, socratic_result: Dict, domain_result: Dict, user_input: str, classification: Dict) -> str:
        """Synthesize focused clarification response"""
        
        if socratic_result and socratic_result.get("response_text"):
            return socratic_result["response_text"]
        
        if domain_result and domain_result.get("response_text"):
            return domain_result["response_text"]
        
        # Fallback clarification response
        return "I understand this can be complex! Let me help clarify. What specific part would you like me to explain in more detail?"
    
    def _synthesize_improvement_response(self, socratic_result: Dict, domain_result: Dict, user_input: str, classification: Dict) -> str:
        """Synthesize focused improvement response"""
        
        if domain_result and domain_result.get("response_text"):
            return domain_result["response_text"]
        
        if socratic_result and socratic_result.get("response_text"):
            return socratic_result["response_text"]
        
        # Fallback improvement response
        return "Great question about improving your design! What specific aspects would you like to enhance? This will help me suggest the most effective improvements."
    
    def _synthesize_challenge_response(self, cognitive_result: Dict, socratic_result: Dict, user_input: str, classification: Dict) -> str:
        """Synthesize focused challenge response"""
        
        if cognitive_result and cognitive_result.get("response_text"):
            return cognitive_result["response_text"]
        
        if socratic_result and socratic_result.get("response_text"):
            return socratic_result["response_text"]
        
        # Fallback challenge response
        return "That's an interesting perspective! Have you considered alternative approaches or potential challenges with your current thinking?"
    
    def _synthesize_general_response(self, socratic_result: Dict, domain_result: Dict, user_input: str, classification: Dict) -> str:
        """Synthesize focused general response"""
        
        if domain_result and domain_result.get("response_text"):
            return domain_result["response_text"]
        
        if socratic_result and socratic_result.get("response_text"):
            return socratic_result["response_text"]
        
        # Fallback general response
        return "That's a great question! I'd be happy to help you explore this further. What specific aspects would you like to focus on?"
        
    # MAIN EXECUTION METHOD
    async def process_student_input(self, student_state: ArchMentorState) -> Dict[str, Any]:
        """Main method to process student input through the full workflow"""

        print("🚀 LangGraph Orchestrator: Starting workflow...")

        # Ensure the brief is the first message if starting a new project
        if student_state.ensure_brief_in_messages():
            # Check if the brief is already in the messages
            if not any(msg.get("role") == "brief" for msg in student_state.messages):
                # Insert the brief as the first message
                student_state.messages.insert(0, {
                    "role": "brief",
                    "content": student_state.current_design_brief
                })

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
    
    # async def process_student_input(self, student_state: ArchMentorState) -> Dict[str, Any]:
    #     """Main method to process student input through the full workflow"""
        
    #     print("🚀 LangGraph Orchestrator: Starting workflow...")
        
    #     # Initialize workflow state
    #     initial_state = WorkflowState(
    #         student_state=student_state,
    #         last_message="",
    #         student_classification={},
    #         routing_decision={},
    #         analysis_result={},
    #         domain_expert_result={},
    #         socratic_result={},
    #         final_response="",
    #         response_metadata={}
    #     )
        
    #     # Execute the workflow
    #     final_state = await self.workflow.ainvoke(initial_state)
        
    #     print("✅ LangGraph workflow completed!")
        
    #     return {
    #         "response": final_state["final_response"],
    #         "metadata": final_state["response_metadata"],
    #         "routing_path": final_state["routing_decision"].get("path", "unknown"),
    #         "classification": final_state["student_classification"]
    #     }

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