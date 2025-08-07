# orchestration/langgraph_orchestrator.py
from typing import Dict, Any, List, Literal, Optional
from langgraph.graph import StateGraph, END
from typing_extensions import TypedDict
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import your agents
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from state_manager import ArchMentorState
from agents.analysis_agent import AnalysisAgent
from agents.socratic_tutor import SocraticTutorAgent
from agents.domain_expert import DomainExpertAgent
from agents.context_agent import ContextAgent
from agents.cognitive_enhancement import CognitiveEnhancementAgent
from config.orchestrator_config import OrchestratorConfig, DEFAULT_CONFIG
from state_manager import*

# Import progressive conversation system
from conversation_progression import ConversationProgressionManager, ConversationPhase
from first_response_generator import FirstResponseGenerator

# Import new routing system
from utils.routing_decision_tree import (
    AdvancedRoutingDecisionTree, 
    RoutingContext, 
    RoutingDecision, 
    RouteType,
    make_advanced_routing_decision
)

# Import state validation system
from utils.state_validator import StateValidator, StateMonitor

class WorkflowState(TypedDict):
    """LangGraph state that flows between agents"""
    # Core state
    student_state: ArchMentorState
    last_message: str
    
    # Context analysis
    student_classification: Dict[str, Any]
    context_analysis: Dict[str, Any]
    routing_decision: Dict[str, Any]
    
    # Agent results
    analysis_result: Dict[str, Any]
    domain_expert_result: Dict[str, Any]
    socratic_result: Dict[str, Any]
    cognitive_enhancement_result: Dict[str, Any] 
    
    # Conversation progression
    conversation_progression: Dict[str, Any]
    #0708-ADDED
    milestone_guidance: Dict[str, Any]  # Milestone-driven guidance for agents
    
    # Final output
    final_response: str
    response_metadata: Dict[str, Any]

class LangGraphOrchestrator:
    def __init__(self, domain="architecture", config: OrchestratorConfig = None):
        self.domain = domain
        self.config = config or DEFAULT_CONFIG
        self.logger = logging.getLogger(f"{__name__}.{domain}")
        
        # Initialize agents
        self.analysis_agent = AnalysisAgent(domain)
        self.socratic_agent = SocraticTutorAgent(domain)
        self.domain_expert = DomainExpertAgent(domain)
        self.cognitive_enhancement_agent = CognitiveEnhancementAgent(domain)
        self.context_agent = ContextAgent(domain)   
        
        # Initialize progressive conversation system
        self.progression_manager = ConversationProgressionManager(domain)
        self.first_response_generator = FirstResponseGenerator(domain)
        
        # Initialize new routing system
        self.routing_decision_tree = AdvancedRoutingDecisionTree()
        
        # Initialize state validation system
        self.state_validator = StateValidator()
        self.state_monitor = StateMonitor()
        
        # Build the workflow graph
        self.workflow = self.build_workflow()
        
        self.logger.info(f"LangGraph orchestrator initialized for {domain}")
    
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
                "progressive_opening": "synthesizer",  # First response goes directly to synthesizer
                "topic_transition": "synthesizer",     # Topic transitions go directly to synthesizer
                "cognitive_intervention": "cognitive_enhancement",
                "socratic_exploration": "socratic_tutor", 
                "design_guidance": "socratic_tutor",   # NEW: Design guidance goes to Socratic tutor
                "multi_agent_comprehensive": "analysis_agent",
                "knowledge_with_challenge": "domain_expert",
                "socratic_clarification": "socratic_tutor",
                "supportive_scaffolding": "socratic_tutor",
                "cognitive_challenge": "cognitive_enhancement",
                "foundational_building": "socratic_tutor",
                "balanced_guidance": "analysis_agent",
                "knowledge_only": "domain_expert",
                "socratic_focus": "analysis_agent",
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
                "to_cognitive": "cognitive_enhancement",  
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
        """Enhanced context agent with progressive conversation support"""
        
        # Validate input state
        validation_result = self.state_validator.validate_state(state["student_state"])
        if not validation_result.is_valid:
            self.logger.warning(f"⚠️ State validation failed in context_agent_node: {validation_result.errors}")
            # Continue with invalid state but log the issues
        
        # Monitor state changes
        self.state_monitor.record_state_change(state["student_state"], "context_agent_node_input")
        
        student_state = state["student_state"]
        last_message = state["last_message"]
        
        self.logger.debug("Context Agent: Processing state with %d messages", len(student_state.messages))
        self.logger.debug("Context Agent: Messages: %s", [msg.get('role', 'unknown') for msg in student_state.messages])
        self.logger.debug("Context Agent: Last user message: %s...", last_message[:50])
        
        # 0708-MILESTONE-DRIVEN CONTEXT ANALYSIS
        # Get milestone guidance for context analysis
        milestone_guidance = state.get("milestone_guidance", {})
        current_milestone = milestone_guidance.get("current_milestone")
        agent_focus = milestone_guidance.get("agent_focus", "context_agent")
        
        self.logger.info(f"🎯 Context Agent - Current milestone: {current_milestone.milestone_type.value if current_milestone else 'None'}")
        self.logger.info(f"🎯 Context Agent - Agent focus: {agent_focus}")
        
        # Check if this is a first message or early conversation
        user_messages = [msg['content'] for msg in student_state.messages if msg.get('role') == 'user']
        
        # RE-ENABLED: Progressive conversation system
        # More precise first message detection
        # Consider it a first message if:
        # 1. No user messages yet, OR
        # 2. Only one user message (the initial design brief) and this is the first follow-up, OR
        # 3. This is a new topic/design brief (topic transition)
        
        # Check if this is the first interactive message after the initial design brief
        # We want to detect when the user is making their first meaningful interactive response
        # This happens when there are exactly two user messages (initial brief + first interactive) and no assistant messages
        # OR when this is the first user message in a new conversation
        is_first_message = len(user_messages) == 0 or (
            len(user_messages) == 2 and 
            student_state.current_design_brief and
            last_message != student_state.current_design_brief and
            len([msg for msg in student_state.messages if msg.get('role') == 'assistant']) == 0
        )
        
        # Debug logging to understand why progressive conversation isn't triggering
        self.logger.info(f"🔍 First Message Detection Debug:")
        self.logger.info(f"   - Total messages in state: {len(student_state.messages)}")
        self.logger.info(f"   - User messages found: {len(user_messages)}")
        self.logger.info(f"   - Is first message: {is_first_message}")
        self.logger.info(f"   - Message roles: {[msg.get('role', 'unknown') for msg in student_state.messages]}")
        
        # Only use progressive opening for truly first messages
        # Topic transitions should be handled by the normal routing logic
        
        if is_first_message:
            # Use progressive conversation system for first response
            self.logger.info("🎯 First message detected - using progressive conversation system")
            
            # Generate progressive first response
            first_response_result = await self.first_response_generator.generate_first_response(last_message, student_state)
            
            # Update state with progression information
            progression_analysis = first_response_result.get("progression_analysis", {})
            
            return {
                **state,
                "last_message": last_message,
                "student_classification": {
                    "interaction_type": "first_message",
                    "understanding_level": progression_analysis.get("user_profile", {}).get("knowledge_level", "unknown"),
                    "confidence_level": "neutral",
                    "engagement_level": "medium",
                    "is_first_message": True
                },
                "context_analysis": {
                    "progression_analysis": progression_analysis,
                    "opening_strategy": first_response_result.get("opening_strategy", {}),
                    "conversation_phase": ConversationPhase.DISCOVERY.value
                },
                "routing_decision": {
                    "path": "progressive_opening",
                    "reasoning": "First message - using progressive conversation system"
                },
                "final_response": first_response_result.get("response_text", ""),
                "response_metadata": first_response_result.get("metadata", {}),
                "progression_data": progression_analysis
            }
            
            # Validate and monitor output state
            result_state = {
                **state,
                "last_message": last_message,
                "student_classification": {
                    "interaction_type": "first_message",
                    "understanding_level": progression_analysis.get("user_profile", {}).get("knowledge_level", "unknown"),
                    "confidence_level": "neutral",
                    "engagement_level": "medium",
                    "is_first_message": True
                },
                "context_analysis": {
                    "progression_analysis": progression_analysis,
                    "opening_strategy": first_response_result.get("opening_strategy", {}),
                    "conversation_phase": ConversationPhase.DISCOVERY.value
                },
                "routing_decision": {
                    "path": "progressive_opening",
                    "reasoning": "First message - using progressive conversation system"
                },
                "final_response": first_response_result.get("response_text", ""),
                "response_metadata": first_response_result.get("metadata", {}),
                "progression_data": progression_analysis
            }
            
            output_validation = self.state_validator.validate_state(result_state["student_state"])
            if not output_validation.is_valid:
                self.logger.warning(f"⚠️ Output state validation failed in context_agent_node: {output_validation.errors}")
            
            self.state_monitor.record_state_change(result_state["student_state"], "context_agent_node_output")
            
            return result_state
        else:
            # Use existing context agent for ongoing conversation
            self.logger.info("🔄 Ongoing conversation - using standard context analysis")
            
            # Use new context agent for comprehensive analysis
            context_package = await self.context_agent.analyze_student_input(student_state, last_message)
            
            # Convert AgentResponse to dictionary if needed
            if hasattr(context_package, 'response_text'):
                context_package = context_package.to_dict()
            
            # Extract classification data from the correct location
            # The context agent stores its data in the metadata field of AgentResponse
            if isinstance(context_package, dict) and "metadata" in context_package:
                # Dictionary format with metadata (converted AgentResponse) - extract from metadata
                original_data = context_package["metadata"]
                core_classification = original_data.get("core_classification", {})
                contextual_metadata = original_data.get("contextual_metadata", {})
                conversation_patterns = original_data.get("conversation_patterns", {})
                routing_suggestions = original_data.get("routing_suggestions", {})
                agent_contexts = original_data.get("agent_contexts", {})
            elif hasattr(context_package, 'metadata'):
                # AgentResponse object - extract from metadata
                original_data = context_package.metadata
                core_classification = original_data.get("core_classification", {})
                contextual_metadata = original_data.get("contextual_metadata", {})
                conversation_patterns = original_data.get("conversation_patterns", {})
                routing_suggestions = original_data.get("routing_suggestions", {})
                agent_contexts = original_data.get("agent_contexts", {})
            else:
                # Dictionary format - access directly (fallback)
                core_classification = context_package.get("core_classification", {})
                contextual_metadata = context_package.get("contextual_metadata", {})
                conversation_patterns = context_package.get("conversation_patterns", {})
                routing_suggestions = context_package.get("routing_suggestions", {})
                agent_contexts = context_package.get("agent_contexts", {})
            
            result_state = {
                **state,
                "last_message": last_message,
                "student_classification": {**core_classification, "last_message": last_message},
                "context_analysis": context_package,  # Store full context analysis
                "context_metadata": contextual_metadata,
                "conversation_patterns": conversation_patterns,
                "routing_suggestions": routing_suggestions,
                "agent_contexts": agent_contexts,
                "context_package": context_package  # Store full package for agents
            }
            
            # Validate and monitor output state
            output_validation = self.state_validator.validate_state(result_state["student_state"])
            if not output_validation.is_valid:
                self.logger.warning(f"⚠️ Output state validation failed in context_agent_node: {output_validation.errors}")
            
            self.state_monitor.record_state_change(result_state["student_state"], "context_agent_node_output")
            
            return result_state
    
    async def router_node(self, state: WorkflowState) -> WorkflowState:
        """ROUTER: Integrated routing using context agent suggestions and orchestrator logic"""
        
        # Validate input state
        validation_result = self.state_validator.validate_state(state["student_state"])
        if not validation_result.is_valid:
            self.logger.warning(f"⚠️ State validation failed in router_node: {validation_result.errors}")
        
        # Monitor state changes
        self.state_monitor.record_state_change(state["student_state"], "router_node_input")
        
        self.logger.info("Router: Determining agent path...")
        
        # Get context agent's analysis and suggestions
        context_analysis = state.get("context_analysis", {})
        routing_suggestions = context_analysis.get("routing_suggestions", {})
        classification = state["student_classification"]
        
        # Store routing suggestions in state for route_decision to use
        state["routing_suggestions"] = routing_suggestions
        
        # Determine the routing path using the route_decision method
        routing_path = self.route_decision(state)
        
        # Create a proper routing_decision dictionary with path and reasoning
        routing_decision = {
            "path": routing_path,
            "reasoning": self._generate_routing_reasoning(routing_path, routing_suggestions, classification)
        }
        
        self.logger.debug("Context agent confidence: %.2f", routing_suggestions.get('confidence', 0))
        self.logger.debug("Interaction type: %s", classification.get('interaction_type', 'unknown'))
        self.logger.info("🎯 Routing decision: %s", routing_path)
        
        result_state = {
            **state,
            "routing_decision": routing_decision
        }
        
        # Validate and monitor output state
        output_validation = self.state_validator.validate_state(result_state["student_state"])
        if not output_validation.is_valid:
            self.logger.warning(f"⚠️ Output state validation failed in router_node: {output_validation.errors}")
        
        self.state_monitor.record_state_change(result_state["student_state"], "router_node_output")
        
        return result_state
    #0708-UPDATED
    async def analysis_agent_node(self, state: WorkflowState) -> WorkflowState:
        """Analysis Agent: Always runs for multi-agent paths with conversation progression integration"""
        
        # Validate input state
        validation_result = self.state_validator.validate_state(state["student_state"])
        if not validation_result.is_valid:
            self.logger.warning(f"⚠️ State validation failed in analysis_agent_node: {validation_result.errors}")
        
        # Monitor state changes
        self.state_monitor.record_state_change(state["student_state"], "analysis_agent_node_input")
        
        self.logger.info("Analysis Agent: Processing with conversation progression...")
        
        student_state = state["student_state"]
        context_package = state.get("context_package", {})
        last_message = state.get("last_message", "")
        
        # Get conversation progression integration
        progression_integration = self.analysis_agent.integrate_conversation_progression(
            student_state, last_message, ""
        )
        
        # Pass context package to analysis agent for better continuity
        analysis_result = await self.analysis_agent.process(student_state, context_package)
        
        # Convert AgentResponse to dictionary if needed
        if hasattr(analysis_result, 'response_text'):
            analysis_result = analysis_result.to_dict()
        
        # Integrate conversation progression data into analysis result
        analysis_result.update({
            "conversation_progression": progression_integration.get("conversation_progression", {}),
            "current_milestone": progression_integration.get("current_milestone"),
            "milestone_assessment": progression_integration.get("milestone_assessment", {}),
            "agent_guidance": progression_integration.get("agent_guidance", {})
        })
        
        result_state = {
            **state,
            "analysis_result": analysis_result,
            "conversation_progression": progression_integration.get("conversation_progression", {}),
            "milestone_guidance": progression_integration.get("agent_guidance", {})
        }
        
        # Validate and monitor output state
        output_validation = self.state_validator.validate_state(result_state["student_state"])
        if not output_validation.is_valid:
            self.logger.warning(f"⚠️ Output state validation failed in analysis_agent_node: {output_validation.errors}")
        
        self.state_monitor.record_state_change(result_state["student_state"], "analysis_agent_node_output")
        
        return result_state
    
    async def domain_expert_node(self, state: WorkflowState) -> WorkflowState:
        """Domain Expert: Knowledge synthesis with visual awareness"""
        
        # Validate input state
        validation_result = self.state_validator.validate_state(state["student_state"])
        if not validation_result.is_valid:
            self.logger.warning(f"⚠️ State validation failed in domain_expert_node: {validation_result.errors}")
        
        # Monitor state changes
        self.state_monitor.record_state_change(state["student_state"], "domain_expert_node_input")
        
        self.logger.info("Domain Expert: Providing knowledge...")
        
        student_state = state["student_state"]
        analysis_result = state.get("analysis_result", {})
        
        # ENHANCED: Pass visual analysis to domain expert for sketch-aware responses
        visual_analysis = analysis_result.get('visual_analysis', {})
        if visual_analysis and not visual_analysis.get('error'):
            self.logger.debug("Domain Expert: Including visual analysis context")
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
            self.logger.debug("Using primary cognitive flag: %s", primary_gap)
        else:
            primary_gap = "brief_development"
            self.logger.debug("Using default: brief development")
        
        domain_result = await self.domain_expert.provide_knowledge(
            student_state, analysis_result, primary_gap
        )
        
        # Convert AgentResponse to dictionary if needed
        if hasattr(domain_result, 'response_text'):
            domain_result = domain_result.to_dict()
        
        result_state = {
            **state,
            "domain_expert_result": domain_result
        }
        
        # Validate and monitor output state
        output_validation = self.state_validator.validate_state(result_state["student_state"])
        if not output_validation.is_valid:
            self.logger.warning(f"⚠️ Output state validation failed in domain_expert_node: {output_validation.errors}")
        
        self.state_monitor.record_state_change(result_state["student_state"], "domain_expert_node_output")
        
        return result_state
    #0708-UPDATED
    async def socratic_tutor_node(self, state: WorkflowState) -> WorkflowState:
        """Socratic Tutor: AI-powered question generation for ANY topic with milestone-driven guidance"""
        
        # Validate input state
        validation_result = self.state_validator.validate_state(state["student_state"])
        if not validation_result.is_valid:
            self.logger.warning(f"⚠️ State validation failed in socratic_tutor_node: {validation_result.errors}")
        
        # Monitor state changes
        self.state_monitor.record_state_change(state["student_state"], "socratic_tutor_node_input")
        
        # 0708-MILESTONE-DRIVEN SOCRATIC GUIDANCE
        milestone_guidance = state.get("milestone_guidance", {})
        current_milestone = milestone_guidance.get("current_milestone")
        agent_guidance = milestone_guidance.get("agent_guidance", {})
        
        self.logger.info(f"🎯 Socratic Tutor - Current milestone: {current_milestone.milestone_type.value if current_milestone else 'None'}")
        self.logger.info(f"🎯 Socratic Tutor - Guidance: {agent_guidance.get('guidance', 'No specific guidance')}")
        
        student_state = state["student_state"]
        analysis_result = state.get("analysis_result", {})
        context_classification = state.get("student_classification", {})
        # ENHANCED: Pass domain expert results to Socratic tutor so it can ask questions about examples
        domain_expert_result = state.get("domain_expert_result", {})
        
        # 0708-Add milestone context to the analysis result for the Socratic agent
        if current_milestone:
            analysis_result["milestone_context"] = {
                "milestone_type": current_milestone.milestone_type.value,
                "phase": current_milestone.phase.value,
                "required_actions": current_milestone.required_actions,
                "success_criteria": current_milestone.success_criteria,
                "agent_guidance": agent_guidance
            }
        
        socratic_result = await self.socratic_agent.generate_response(
            student_state, analysis_result, context_classification, domain_expert_result
        )
        
        # Convert AgentResponse to dictionary if needed
        if hasattr(socratic_result, 'response_text'):
            socratic_result = socratic_result.to_dict()
        
        result_state = {
            **state,
            "socratic_result": socratic_result
        }
        
        # Validate and monitor output state
        output_validation = self.state_validator.validate_state(result_state["student_state"])
        if not output_validation.is_valid:
            self.logger.warning(f"⚠️ Output state validation failed in socratic_tutor_node: {output_validation.errors}")
        
        self.state_monitor.record_state_change(result_state["student_state"], "socratic_tutor_node_output")
        
        return result_state

    
    async def cognitive_enhancement_node(self, state: WorkflowState) -> WorkflowState:
        """Cognitive Enhancement Agent node"""
        
        # Validate input state
        validation_result = self.state_validator.validate_state(state["student_state"])
        if not validation_result.is_valid:
            self.logger.warning(f"⚠️ State validation failed in cognitive_enhancement_node: {validation_result.errors}")
        
        # Monitor state changes
        self.state_monitor.record_state_change(state["student_state"], "cognitive_enhancement_node_input")
        
        self.logger.info("Cognitive Enhancement Agent: Enhancing cognition...")
        
        student_state = state["student_state"]
        analysis_result = state.get("analysis_result", {})
        context_classification = state.get("student_classification", {})
        routing_decision = state.get("routing_decision", {})
        
        # Use all 4 parameters as expected by the agent
        enhancement_result = await self.cognitive_enhancement_agent.provide_challenge(
            student_state, context_classification, analysis_result, routing_decision
        )
        
        # Convert AgentResponse to dictionary if needed
        if hasattr(enhancement_result, 'response_text'):
            enhancement_result = enhancement_result.to_dict()
        
        self.logger.debug("Generated enhancement result: %s", enhancement_result)
        
        result_state = {
            **state,
            "cognitive_enhancement_result": enhancement_result
        }
        
        # Validate and monitor output state
        output_validation = self.state_validator.validate_state(result_state["student_state"])
        if not output_validation.is_valid:
            self.logger.warning(f"⚠️ Output state validation failed in cognitive_enhancement_node: {output_validation.errors}")
        
        self.state_monitor.record_state_change(result_state["student_state"], "cognitive_enhancement_node_output")
        
        return result_state
    
    async def synthesizer_node(self, state: WorkflowState) -> WorkflowState:
        """Synthesizer: Combines all agent outputs (Section 7)"""
        
        # Validate input state
        validation_result = self.state_validator.validate_state(state["student_state"])
        if not validation_result.is_valid:
            self.logger.warning(f"⚠️ State validation failed in synthesizer_node: {validation_result.errors}")
        
        # Monitor state changes
        self.state_monitor.record_state_change(state["student_state"], "synthesizer_node_input")
        
        self.logger.info("Synthesizer: Combining agent responses...")
        
        # Check if we already have a final_response (progressive conversation paths)
        existing_response = state.get("final_response", "")
        if existing_response:
            self.logger.info("🎯 Using existing progressive response - skipping synthesis")
            metadata = state.get("response_metadata", {})
            
            # HYBRID APPROACH: Add milestone question if needed
            milestone_question = await self._add_milestone_question_if_needed(state, existing_response)
            if milestone_question:
                existing_response += f"\n\n🎯 **Milestone Question:** {milestone_question}"
            
            result_state = {
                **state,
                "final_response": existing_response,
                "response_metadata": metadata
            }
            
            # Validate and monitor output state
            output_validation = self.state_validator.validate_state(result_state["student_state"])
            if not output_validation.is_valid:
                self.logger.warning(f"⚠️ Output state validation failed in synthesizer_node: {output_validation.errors}")
            
            self.state_monitor.record_state_change(result_state["student_state"], "synthesizer_node_output")
            
            return result_state
        
        # Standard synthesis for multi-agent paths
        self.logger.debug("cognitive_enhancement_result: %s", state.get("cognitive_enhancement_result"))
        final_response, metadata = self.synthesize_responses(state)
        
        # HYBRID APPROACH: Add milestone question if needed
        milestone_question = await self._add_milestone_question_if_needed(state, final_response)
        if milestone_question:
            final_response += f"\n\n🎯 **Milestone Question:** {milestone_question}"
        
        result_state = {
            **state,
            "final_response": final_response,
            "response_metadata": metadata
        }
        
        # Validate and monitor output state
        output_validation = self.state_validator.validate_state(result_state["student_state"])
        if not output_validation.is_valid:
            self.logger.warning(f"⚠️ Output state validation failed in synthesizer_node: {output_validation.errors}")
        
        self.state_monitor.record_state_change(result_state["student_state"], "synthesizer_node_output")
        
        return result_state
    
    # ROUTING LOGIC
    def route_decision(self, state: WorkflowState) -> str:
        """Enhanced routing using AdvancedRoutingDecisionTree"""
        
        classification = state.get("student_classification", {})
        context_analysis = state.get("context_analysis", {})
        routing_suggestions = state.get("routing_suggestions", {})
        routing_decision = state.get("routing_decision", {})
        student_state = state.get("student_state", None)
        
        # Create routing context
        routing_context = RoutingContext(
            classification=classification,
            context_analysis=context_analysis,
            routing_suggestions=routing_suggestions,
            student_state=student_state.__dict__ if student_state else None,
            conversation_history=student_state.messages if student_state else [],
            current_phase=student_state.design_phase.value if student_state else "ideation",
            phase_progress=0.0  # Default value since ArchMentorState doesn't have phase_progress
        )
        
        # Use the advanced routing decision tree
        decision = self.routing_decision_tree.decide_route(routing_context)
        
        # Store the decision for reasoning method
        self.last_routing_decision = decision
        
        # Log the routing decision
        self.logger.info(f"🎯 Advanced Routing Decision: {decision.route.value}")
        self.logger.info(f"   Reason: {decision.reason}")
        self.logger.info(f"   Confidence: {decision.confidence:.2f}")
        self.logger.info(f"   Rule Applied: {decision.rule_applied}")
        
        # Store the detailed decision in state for later use
        state["detailed_routing_decision"] = {
            "route": decision.route.value,
            "reason": decision.reason,
            "confidence": decision.confidence,
            "rule_applied": decision.rule_applied,
            "context_agent_override": decision.context_agent_override,
            "cognitive_offloading_detected": decision.cognitive_offloading_detected,
            "cognitive_offloading_type": decision.cognitive_offloading_type.value if decision.cognitive_offloading_type else None,
            "context_agent_confidence": decision.context_agent_confidence,
            "classification": decision.classification,
            "metadata": decision.metadata
        }
        
        return decision.route.value
    
    def _generate_routing_reasoning(self, routing_path: str, routing_suggestions: Dict[str, Any], classification: Dict[str, Any]) -> str:
        """Generate human-readable reasoning for the routing decision using advanced routing system"""
        
        # Check if we have a detailed routing decision from the advanced system
        if hasattr(self, 'last_routing_decision') and self.last_routing_decision:
            return self.last_routing_decision.reason
        
        # Fallback to original reasoning logic
        # If we have context agent suggestions with high confidence, use them
        if routing_suggestions and routing_suggestions.get("confidence", 0) > 0.6:
            primary_route = routing_suggestions.get("primary_route", "default")
            confidence = routing_suggestions.get("confidence", 0)
            return f"Context agent suggested '{primary_route}' with {confidence:.1%} confidence, mapped to '{routing_path}'"
        
        # Generate reasoning based on classification
        interaction_type = classification.get("interaction_type", "general_statement")
        confidence_level = classification.get("confidence_level", "confident")
        understanding_level = classification.get("understanding_level", "medium")
        
        reasoning_parts = []
        
        # Interaction type reasoning
        if interaction_type == "example_request":
            reasoning_parts.append("User requested examples")
        elif interaction_type == "feedback_request":
            reasoning_parts.append("User requested feedback")
        elif interaction_type == "technical_question":
            reasoning_parts.append("User asked technical question")
        elif interaction_type == "confusion_expression":
            reasoning_parts.append("User expressed confusion")
        
        # Confidence level reasoning
        if confidence_level == "overconfident":
            reasoning_parts.append("User appears overconfident")
        elif confidence_level == "uncertain":
            reasoning_parts.append("User appears uncertain")
        
        # Understanding level reasoning
        if understanding_level == "low":
            reasoning_parts.append("User has low understanding")
        elif understanding_level == "high":
            reasoning_parts.append("User has high understanding")
        
        # Route-specific reasoning
        if routing_path == "cognitive_intervention":
            reasoning_parts.append("Cognitive offloading detected")
        elif routing_path == "knowledge_only":
            reasoning_parts.append("Pure knowledge request identified")
        elif routing_path == "socratic_exploration":
            reasoning_parts.append("Exploration/guidance needed")
        elif routing_path == "multi_agent_comprehensive":
            reasoning_parts.append("Complex request requiring multiple agents")
        elif routing_path == "socratic_clarification":
            reasoning_parts.append("Clarification needed")
        elif routing_path == "supportive_scaffolding":
            reasoning_parts.append("Supportive scaffolding needed")
        elif routing_path == "foundational_building":
            reasoning_parts.append("Foundational knowledge needed")
        elif routing_path == "knowledge_with_challenge":
            reasoning_parts.append("Knowledge with challenge needed")
        elif routing_path == "balanced_guidance":
            reasoning_parts.append("Balanced guidance approach")
        elif routing_path == "design_guidance":
            reasoning_parts.append("Design guidance requested")
        elif routing_path == "progressive_opening":
            reasoning_parts.append("Progressive conversation opening")
        elif routing_path == "topic_transition":
            reasoning_parts.append("Topic transition detected")
        
        if reasoning_parts:
            return f"Route '{routing_path}' selected based on: {', '.join(reasoning_parts)}"
        else:
            return f"Route '{routing_path}' selected as default balanced guidance"
    def _detect_cognitive_offloading(self, classification: Dict, context_analysis: Dict) -> Dict[str, Any]:
        """Detect cognitive offloading patterns - aligned with context agent logic"""
        
        offloading_indicators = {
            "detected": False,
            "type": None,
            "confidence": 0.0,
            "indicators": []
        }
        
        # PATTERN 1: Direct answer seeking without exploration (but NOT legitimate example requests)
        if classification.get("interaction_type") == "feedback_request":
            recent_messages = context_analysis.get("conversation_patterns", {}).get("recent_messages", [])
            if len(recent_messages) < 3:  # New conversation
                offloading_indicators["detected"] = True
                offloading_indicators["type"] = "premature_answer_seeking"
                offloading_indicators["confidence"] = 0.8
                offloading_indicators["indicators"].append("Asking for answers before exploration")
        
        # PATTERN 2: Overconfidence with low engagement
        if (classification.get("confidence_level") == "overconfident" and 
            classification.get("engagement_level") == "low"):
            offloading_indicators["detected"] = True
            offloading_indicators["type"] = "superficial_confidence"
            offloading_indicators["confidence"] = 0.7
            offloading_indicators["indicators"].append("Overconfident but not engaged")
        
        # PATTERN 3: Repetitive question patterns (aligned with context agent logic)
        patterns = context_analysis.get("conversation_patterns", {})
        if patterns.get("repetitive_topics", False):
            # Check if this is a legitimate response to a question (not repetitive dependency)
            interaction_type = classification.get("interaction_type", "")
            
            # ENHANCED: More nuanced detection - don't flag legitimate follow-up questions
            if interaction_type != "question_response":  # Only flag if not responding to a question
                # ADDITIONAL CHECK: Don't flag knowledge_seeking questions as repetitive dependency
                # These are legitimate follow-up questions that deserve direct answers
                if interaction_type == "knowledge_seeking":
                    self.logger.debug("✅ Knowledge seeking question - not flagging as repetitive dependency")
                    return offloading_indicators
                
                # ADDITIONAL CHECK: Don't flag if the question is about a different aspect
                # (e.g., "circulation" vs "lighting" are different aspects of design)
                user_input = classification.get("last_message", "").lower()
                if any(word in user_input for word in ["circulation", "lighting", "structure", "materials", "program", "context"]):
                    self.logger.debug("✅ Different design aspect question - not flagging as repetitive dependency")
                    return offloading_indicators
                
                offloading_indicators["detected"] = True
                offloading_indicators["type"] = "repetitive_dependency"
                offloading_indicators["confidence"] = 0.6
                offloading_indicators["indicators"].append("Repeating same questions")
        
        return offloading_indicators
    
    # Fix after_analysis_routing method

    def after_analysis_routing(self, state: WorkflowState) -> str:
        """Simplified routing after analysis that ensures comprehensive responses"""
        
        self.logger.info("🎯 After analysis routing...")
        
        # For comprehensive responses, we want domain expert, Socratic tutor, and cognitive enhancement
        # The workflow will execute them in sequence
        
        self.logger.info("🚀 Will execute: domain_expert → socratic_tutor → cognitive_enhancement → synthesizer")
        return "to_domain_expert"
    
    def after_domain_expert(self, state: WorkflowState) -> Literal["to_socratic", "to_synthesizer"]:
        """Route after domain expert based on the original request type"""
        
        # Check if this was a knowledge_only request
        routing_decision = state.get("routing_decision", {})
        original_path = routing_decision.get("path", "default")
        
        # The Socratic Tutor should ask questions about the examples that were just provided
        self.logger.info("🎯 After domain expert: Going to Socratic tutor to ask questions about provided examples")
        return "to_socratic"
    
    def after_socratic_tutor(self, state: WorkflowState) -> Literal["to_cognitive", "to_synthesizer"]:
        """Always go to cognitive enhancement after Socratic tutor for comprehensive responses"""
        
        self.logger.info("🎯 After Socratic tutor: Going to cognitive enhancement...")
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
        
    #Fix classify_student_input method

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

        # 2. Confidence Level
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

        # 4. Interaction Type
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

        self.logger.debug(f"      🔍 Classification Debug:")
        self.logger.debug(f"         Overconfidence score: {overconfidence_score}")
        self.logger.debug(f"         Is feedback request: {is_feedback_request}")
        self.logger.debug(f"         Is technical question: {is_technical_question}")
        self.logger.debug(f"         Is example request: {is_example_request}")
        self.logger.debug(f"         Confidence level: {confidence}")

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


    # COMPLETE FIX for determine_routing method
    async def determine_routing(self, routing_suggestions: Dict[str, Any], classification: Dict[str, Any], state: ArchMentorState = None) -> Dict[str, Any]:
        """Enhanced routing with better Socratic integration for design guidance"""

        # FIRST: Check if this is a continuation of an ongoing conversation thread
        if state and len(state.messages) >= 2:
            thread_continuation = await self._check_conversation_thread(state, classification)
            if thread_continuation:
                self.logger.info(f"🔗 Continuing conversation thread: {thread_continuation['reason']}")
                return thread_continuation

        # Check if user is responding to a question
        interaction_type = classification.get("interaction_type", "")
        if interaction_type == "question_response":
            self.logger.info(f"✅ QUESTION RESPONSE DETECTED: '{classification.get('last_message', '')}' → socratic_exploration")
            return {
                "path": "socratic_exploration",
                "agents_to_activate": ["socratic_tutor", "domain_expert"],
                "reason": "User is responding to a question - continue exploration",
                "confidence": 0.95
            }

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
            self.logger.info(f"✅ PURE EXAMPLE REQUEST: '{last_message}' → knowledge_only")
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
            self.logger.info(f"🤔 DESIGN DECISION REQUEST: '{last_message}' → socratic_focus")
            return {
                "path": "socratic_focus",
                "agents_to_activate": ["socratic_tutor"],
                "reason": "Design decision question needs Socratic guidance to help student think through options",
                "confidence": 0.95
            }
        
        # --- DESIGN GUIDANCE REQUEST DETECTION (default = Knowledge + Socratic) ---
        design_guidance_patterns = [
            "how can i", "how do i", "how to", "how might", "how should",
            "what direction should", "what direction", "where should", "which direction",
            "what's the best way", "what are ways to", "approaches to",
            "incorporate", "integrate", "implement", "apply", "use",
            "design", "create", "make", "develop", "enhance", "improve"
        ]
        
        is_design_guidance_request = any(pattern in last_message.lower() for pattern in design_guidance_patterns)
        
        if is_design_guidance_request:
            self.logger.info(f"🎯 DESIGN GUIDANCE REQUEST: '{last_message}' → default (Knowledge + Socratic)")
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

        self.logger.debug(f"📊 Classification: {confidence_level} confidence, {understanding_level} understanding, {engagement_level} engagement")
        self.logger.debug(f"📊 Interaction type: {classification.get('interaction_type', 'unknown')}")
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

        self.logger.info(f"✅ Route chosen: {routing_decision['path']}")
        self.logger.info(f"🤖 Agents to activate: {routing_decision['agents_to_activate']}")

        return routing_decision


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

        # --- ENHANCED FOLLOW-UP DETECTION ---
        # Check for design guidance patterns first (higher priority)
        design_guidance_patterns = [
            "what direction", "how should i", "how can i", "how do i", "how to",
            "what should i", "where should", "which direction", "how might",
            "what's the best way", "what are ways to", "approaches to",
            "incorporate", "integrate", "implement", "apply", "use",
            "design", "create", "make", "develop", "enhance", "improve",
            "circulation", "lighting", "spatial", "organization", "layout"
        ]
        
        if any(pattern in current_user_msg.lower() for pattern in design_guidance_patterns):
            self.logger.info("🔗 Detected follow-up design guidance request")
            return {
                "path": "design_guidance",
                "agents_to_activate": ["socratic_tutor", "domain_expert"],
                "reason": "User asking for design guidance - provide Socratic guidance",
                "confidence": 0.95,
                "thread_type": "followup_design_guidance"
            }
        
        # Check for example requests (lower priority)
        followup_example_patterns = [
            "another example", "more examples", "different example", "other example",
            "another project", "more projects", "different project", "other projects", 
            "another precedent", "more precedents", "different precedent", "other precedents",
            "can you give another", "can you show another", "can you provide another",
            "give me another", "show me another", "any other", "what about another"
        ]
        
        if any(pattern in current_user_msg.lower() for pattern in followup_example_patterns):
            self.logger.info("🔗 Detected follow-up example/project/precedent request")
            return {
                "path": "default",
                "agents_to_activate": ["domain_expert", "socratic_tutor"],
                "reason": "User requested additional examples/projects/precedents - provide with Socratic guidance",
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
            5. Asking for design guidance (how to do something, what direction, etc.)

            Respond with ONLY:
            - "EXAMPLE_REQUEST" if requesting examples/projects/precedents
            - "DESIGN_GUIDANCE" if asking for design advice/guidance
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

            self.logger.info(f"🧠 AI Thread Detection: {thread_type}")

            # Route based on AI detection
            if thread_type == "DESIGN_GUIDANCE":
                return {
                    "path": "design_guidance",
                    "agents_to_activate": ["socratic_tutor", "domain_expert"],
                    "reason": "AI detected: User asking for design guidance - provide Socratic guidance",
                    "confidence": 0.95,
                    "thread_type": "ai_design_guidance"
                }
            elif thread_type == "EXAMPLE_REQUEST":
                return {
                    "path": "default",
                    "agents_to_activate": ["domain_expert", "socratic_tutor"],
                    "reason": "AI detected: User requesting examples/references - provide with Socratic guidance",
                    "confidence": 0.95,
                    "thread_type": "ai_example_continuation"
                }
            elif thread_type == "ANSWER_CONTINUATION":
                return {
                    "path": "socratic_exploration", 
                    "agents_to_activate": ["socratic_tutor", "domain_expert"],
                    "reason": "AI detected: User answered system's question - continue Socratic exploration",
                    "confidence": 0.9,
                    "thread_type": "ai_answer_continuation"
                }
            elif thread_type == "TOPIC_CONTINUATION":
                return {
                    "path": "default",
                    "agents_to_activate": ["domain_expert", "socratic_tutor"], 
                    "reason": "AI detected: User continuing topic exploration - provide comprehensive guidance",
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
            self.logger.error(f"⚠️ AI thread detection failed: {e}")
            return None








    #execution helper method
    async def execute_agent_sequence(self, state: WorkflowState) -> WorkflowState:
        """Execute agents based on routing decision"""
        
        routing = state.get("routing_decision", {})
        path = routing.get("path", "default")
        agents_to_activate = routing.get("agents_to_activate", [])
        
        self.logger.info(f"🚀 Executing {path} path with agents: {agents_to_activate}")
        
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
    #3107-FULL DEFINITION ENHANCED SYNTHESIZE RESPONSES
    def synthesize_responses(self, state: WorkflowState) -> tuple[str, Dict[str, Any]]:
        """Enhanced response synthesis that uses routing-specific methods"""
        
        self.logger.info("Synthesizing responses...")
        
        # Extract all data from state
        agent_results = self._get_agent_results(state)
        routing_decision = state.get("routing_decision", {})
        user_input = state.get("last_message", "")
        classification = state.get("student_classification", {})
        
        self.logger.debug("Available results: socratic=%s, domain=%s, cognitive=%s", 
                         bool(agent_results.get("socratic")), 
                         bool(agent_results.get("domain")), 
                         bool(agent_results.get("cognitive")))
        self.logger.debug("Routing path: %s", routing_decision.get('path', 'unknown'))
        
        # Extract individual results for easier access
        domain_result = agent_results.get("domain", {})
        socratic_result = agent_results.get("socratic", {})
        cognitive_result = agent_results.get("cognitive", {})
        
        # Determine response type and synthesize
        routing_path = routing_decision.get("path", "default")
        final_response, response_type = self._synthesize_by_routing_path(
            routing_path, agent_results, user_input, classification, state
        )
        
        # Create sophisticated response by combining domain knowledge with Socratic guidance
        if domain_result and socratic_result:
            # Both domain knowledge and Socratic guidance available
            domain_text = domain_result.get("response_text", "")
            socratic_text = socratic_result.get("response_text", "")
            
            final_response = f"{domain_text}\n\n{socratic_text}"
            response_type = "multi_agent_synthesis"
            
        elif domain_result:
            # Only domain knowledge available
            final_response = domain_result.get("response_text", "")
            response_type = "domain_knowledge"
            
        elif socratic_result:
            # Only Socratic guidance available
            socratic_text = socratic_result.get("response_text", "")
            
            # Don't add cognitive assessment to keep response clean
            final_response = socratic_text
                
            response_type = "socratic_guidance"
            
        elif cognitive_result:
            # Only cognitive enhancement available
            cognitive_text = cognitive_result.get("response_text", "")
            
            # Use only the detailed response, not the summary
            final_response = cognitive_text
            response_type = "cognitive_enhancement"
            
        else:
            # Fallback response
            final_response = "I'd be happy to help you with your architectural project. What specific aspect would you like to explore?"
            response_type = "fallback"
        
        # Don't add cognitive assessment to keep responses clean
        # The cognitive data is still tracked in metadata for analysis
        
        # Build metadata
        metadata = self._build_metadata(response_type, agent_results, routing_decision, classification)
        
        # Print summary if enabled
        self._print_summary_if_enabled(state, response_type, metadata)
        
        return final_response, metadata
    
    def _get_agent_results(self, state: WorkflowState) -> Dict[str, Any]:
        """Extract all agent results from state"""
        return {
            "socratic": state.get("socratic_result", {}),
            "domain": state.get("domain_expert_result", {}),
            "analysis": state.get("analysis_result", {}),
            "cognitive": state.get("cognitive_enhancement_result", {})
        }
    
    def _synthesize_by_routing_path(self, routing_path: str, agent_results: Dict[str, Any], 
                                   user_input: str, classification: Dict, state: WorkflowState) -> tuple[str, str]:
        """Synthesize response based on specific routing path"""
        
        # PRIORITY: Progressive conversation paths
        if routing_path in ["progressive_opening", "topic_transition"]:
            # Use the progressive response that was already generated and stored in state
            final_response = state.get("final_response", "")
            if final_response:
                self.logger.info(f"🎯 Using progressive conversation response for path: {routing_path}")
                return final_response, "progressive_opening"
            else:
                self.logger.warning(f"⚠️ Progressive response not found for path: {routing_path}, falling back to default")
                return self._synthesize_default_response(agent_results)
        
        elif routing_path == "knowledge_only":
            return self._synthesize_knowledge_only_response(agent_results, user_input, classification)
        elif routing_path == "socratic_exploration":
            return self._synthesize_socratic_exploration_response(agent_results)
        elif routing_path == "cognitive_intervention":
            return self._synthesize_cognitive_intervention_response(agent_results)
        elif routing_path == "technical_question":
            domain_result = agent_results.get("domain", {})
            return self._synthesize_technical_response(domain_result, user_input, classification)
        elif routing_path == "feedback_request":
            socratic_result = agent_results.get("socratic", {})
            domain_result = agent_results.get("domain", {})
            return self._synthesize_feedback_response(socratic_result, domain_result, user_input, classification)
        elif routing_path == "design_guidance":
            return self._synthesize_design_guidance_response(agent_results, user_input, classification)
        else:
            return self._synthesize_default_response(agent_results)
    
    def _synthesize_knowledge_only_response(self, agent_results: Dict[str, Any], 
                                          user_input: str, classification: Dict) -> tuple[str, str]:
        """Synthesize knowledge-only response with optional Socratic questions"""
        domain_result = agent_results.get("domain", {})
        socratic_result = agent_results.get("socratic", {})
        
        if domain_result and socratic_result:
            domain_text = domain_result.get("response_text", "")
            socratic_text = socratic_result.get("response_text", "")
            final_response = f"{domain_text}\n\n{socratic_text}"
            response_type = "knowledge_only_with_socratic"
            self.logger.debug("Combining examples + Socratic questions about examples")
        else:
            final_response = self._synthesize_example_response(domain_result, user_input, classification)
            response_type = "knowledge_only"
            self.logger.debug("Using knowledge_only synthesis (examples only)")
        
        return final_response, response_type
    
    def _synthesize_socratic_exploration_response(self, agent_results: Dict[str, Any]) -> tuple[str, str]:
        """Synthesize Socratic exploration response"""
        socratic_result = agent_results.get("socratic", {})
        
        if socratic_result and socratic_result.get("response_text"):
            final_response = socratic_result.get("response_text", "")
        else:
            final_response = "I'd be happy to help you explore this topic together. What specific aspects would you like to think about?"
        
        self.logger.debug("Using socratic_exploration synthesis")
        return final_response, "socratic_exploration"
    
    def _synthesize_cognitive_intervention_response(self, agent_results: Dict[str, Any]) -> tuple[str, str]:
        """Synthesize cognitive intervention response"""
        cognitive_result = agent_results.get("cognitive", {})
        
        if cognitive_result and cognitive_result.get("response_text"):
            final_response = cognitive_result.get("response_text", "")
        else:
            final_response = "I notice you're asking for specific answers early in your design process. Let's explore this together instead."
        
        self.logger.debug("Using cognitive_intervention synthesis")
        return final_response, "cognitive_intervention"
    
    def _synthesize_default_response(self, agent_results: Dict[str, Any]) -> tuple[str, str]:
        """Synthesize default comprehensive response"""
        domain_result = agent_results.get("domain", {})
        socratic_result = agent_results.get("socratic", {})
        cognitive_result = agent_results.get("cognitive", {})
        
        if domain_result and socratic_result:
            domain_text = domain_result.get("response_text", "")
            socratic_text = socratic_result.get("response_text", "")
            final_response = f"{domain_text}\n\n{socratic_text}"
            response_type = "multi_agent_synthesis"
            self.logger.debug("Combining domain knowledge + Socratic guidance")
        elif domain_result:
            final_response = domain_result.get("response_text", "")
            response_type = "domain_knowledge"
            self.logger.debug("Using domain knowledge only")
        elif socratic_result:
            final_response = socratic_result.get("response_text", "")
            response_type = "socratic_guidance"
            self.logger.debug("Using Socratic guidance only")
        elif cognitive_result:
            final_response = cognitive_result.get("response_text", "")
            response_type = "cognitive_enhancement"
            self.logger.debug("Using cognitive enhancement only")
        else:
            final_response = "I'd be happy to help you with your architectural project. What specific aspect would you like to explore?"
            response_type = "fallback"
            self.logger.debug("Using fallback response")
        
        return final_response, response_type
    
    def _add_cognitive_metrics_if_enabled(self, final_response: str, cognitive_result: Dict, 
                                         student_state: Any, response_type: str) -> str:
        """Add cognitive assessment to response if enabled in settings"""
        if not cognitive_result:
            return final_response
            
        show_metrics = getattr(student_state, 'show_scientific_metrics', False)
        cognitive_summary = cognitive_result.get("cognitive_summary")
        
        if (show_metrics and cognitive_summary and 
            response_type not in ["cognitive_enhancement", "socratic_guidance", "cognitive_intervention"]):
            final_response = f"{final_response}\n\n{cognitive_summary}"
            self.logger.debug("Added cognitive assessment to %s response", response_type)
        
        return final_response
    
    def _build_metadata(self, response_type: str, agent_results: Dict[str, Any], 
                       routing_decision: Dict, classification: Dict) -> Dict[str, Any]:
        """Build comprehensive metadata for the response"""
        
        # Determine which agents were used
        agents_used = []
        if agent_results.get("socratic"):
            agents_used.append("socratic_tutor")
        if agent_results.get("domain"):
            agents_used.append("domain_expert")
        if agent_results.get("analysis"):
            agents_used.append("analysis_agent")
        if agent_results.get("cognitive"):
            agents_used.append("cognitive_enhancement")
        
        # Extract analysis data
        analysis_result = agent_results.get("analysis", {})
        cognitive_result = agent_results.get("cognitive", {})
        domain_result = agent_results.get("domain", {})
        
        return {
            "response_type": response_type,
            "agents_used": agents_used,
            "routing_path": routing_decision.get("path", "unknown"),
            "ai_reasoning": routing_decision.get("reasoning", "No AI reasoning available"),
            "phase_analysis": analysis_result.get("phase_analysis", {}),
            "scientific_metrics": cognitive_result.get("scientific_metrics", {}),
            "cognitive_state": cognitive_result.get("cognitive_state", {}),
            "analysis_result": analysis_result,
            "sources": domain_result.get("sources", []) if domain_result else [],
            "processing_time": "N/A",  # Will be set by the orchestrator
            "classification": classification
        }
    
    def _print_summary_if_enabled(self, state: WorkflowState, response_type: str, metadata: Dict[str, Any]) -> None:
        """Print comprehensive summary if enabled in student state"""
        student_state = state.get("student_state", {})
        
        if hasattr(student_state, 'show_response_summary') and student_state.show_response_summary:
            self._print_response_summary(
                user_input=state.get("last_message", ""),
                response_type=response_type,
                agents_used=metadata.get("agents_used", []),
                routing_path=metadata.get("routing_path", "unknown"),
                classification=metadata.get("classification", {}),
                phase_analysis=metadata.get("phase_analysis", {}),
                cognitive_state=metadata.get("cognitive_state", {}),
                sources=metadata.get("sources", [])
            )
    
    def _print_response_summary(self, user_input: str, response_type: str, agents_used: List[str], 
                               routing_path: str, classification: Dict, phase_analysis: Dict, 
                               cognitive_state: Dict, sources: List[str]) -> None:
        """Print a comprehensive summary of the response processing"""
        
        self.logger.info("\n" + "="*80)
        self.logger.info("🎯 RESPONSE PROCESSING SUMMARY")
        self.logger.info("="*80)
        
        # User Input
        self.logger.info(f"📝 USER INPUT: {user_input[:100]}{'...' if len(user_input) > 100 else ''}")
        
        # Classification
        self.logger.info(f"\n🔍 CLASSIFICATION:")
        self.logger.info(f"   • Interaction Type: {classification.get('interaction_type', 'unknown')}")
        self.logger.info(f"   • Understanding Level: {classification.get('understanding_level', 'unknown')}")
        self.logger.info(f"   • Confidence Level: {classification.get('confidence_level', 'unknown')}")
        self.logger.info(f"   • Engagement Level: {classification.get('engagement_level', 'unknown')}")
        
        # Routing
        self.logger.info(f"\n🛣️  ROUTING:")
        self.logger.info(f"   • Path: {routing_path}")
        self.logger.info(f"   • Response Type: {response_type}")
        self.logger.info(f"   • Agents Used: {', '.join(agents_used) if agents_used else 'None'}")
        
        # Phase Analysis
        if phase_analysis:
            self.logger.info(f"\n📊 PHASE ANALYSIS:")
            self.logger.info(f"   • Current Phase: {phase_analysis.get('phase', 'unknown')}")
            self.logger.info(f"   • Confidence: {phase_analysis.get('confidence', 0):.1%}")
            self.logger.info(f"   • Indicators: {', '.join(phase_analysis.get('indicators', []))}")
        
        # Cognitive State
        if cognitive_state:
            self.logger.info(f"\n🧠 COGNITIVE STATE:")
            self.logger.info(f"   • Engagement: {cognitive_state.get('engagement_level', 'unknown')}")
            self.logger.info(f"   • Cognitive Load: {cognitive_state.get('cognitive_load_level', 'unknown')}")
            self.logger.info(f"   • Metacognitive Awareness: {cognitive_state.get('metacognitive_awareness', 'unknown')}")
            self.logger.info(f"   • Learning Progression: {cognitive_state.get('learning_progression', 'unknown')}")
        
        # Sources (if any)
        if sources:
            self.logger.info(f"\n📚 SOURCES:")
            for i, source in enumerate(sources[:3], 1):  # Show first 3 sources
                self.logger.info(f"   {i}. {source}")
            if len(sources) > 3:
                self.logger.info(f"   ... and {len(sources) - 3} more")
        
        # Cognitive Offloading Detection
        if classification.get('cognitive_offloading_detected'):
            offloading = classification.get('cognitive_offloading_flags', {})
            self.logger.info(f"\n🛡️  COGNITIVE PROTECTION:")
            self.logger.info(f"   • Detected: {offloading.get('type', 'unknown')}")
            self.logger.info(f"   • Confidence: {offloading.get('confidence', 0):.1%}")
            self.logger.info(f"   • Mitigation: {offloading.get('mitigation_strategy', 'none')}")
        
        self.logger.info("="*80)
        self.logger.info("✅ RESPONSE COMPLETE")
        self.logger.info("="*80 + "\n")
    
    def _print_user_requested_info(self, final_state: WorkflowState) -> None:
        """Print only the specific information requested by user: route, interaction type, response type, AI reasoning"""
        
        # Extract information from final state
        routing_path = final_state["routing_decision"].get("path", "unknown")
        classification = final_state["student_classification"]
        response_type = final_state["response_metadata"].get("response_type", "unknown")
        ai_reasoning = final_state["response_metadata"].get("ai_reasoning", "No AI reasoning available")
        
        # Print the requested information as a small list
        print("\n" + "─" * 50)
        print("📋 PROCESS SUMMARY")
        print("─" * 50)
        print(f"🛣️  Route: {routing_path}")
        print(f"💬 Interaction Type: {classification.get('interaction_type', 'unknown')}")
        print(f"📝 Response Type: {response_type}")
        print(f"🤖 AI Reasoning: {ai_reasoning[:100]}{'...' if len(ai_reasoning) > 100 else ''}")
        print("─" * 50)
        
        # Print very short process overview
        print("\n⚡ PROCESS OVERVIEW:")
        agents_used = []
        if final_state.get("analysis_result"):
            agents_used.append("Analysis")
        if final_state.get("domain_expert_result"):
            agents_used.append("Domain Expert")
        if final_state.get("socratic_result"):
            agents_used.append("Socratic Tutor")
        if final_state.get("cognitive_enhancement_result"):
            agents_used.append("Cognitive Enhancement")
        
        print(f"   Agents used: {', '.join(agents_used) if agents_used else 'None'}")
        print(f"   Processing time: {final_state['response_metadata'].get('processing_time', 'N/A')}")
        print("─" * 50 + "\n")
    
    #3107-SOCRATIC ADDED TO EXAMPLE RESPONSE
    def _synthesize_design_guidance_response(self, agent_results: Dict[str, Any], user_input: str, classification: Dict) -> str:
        """Synthesize design guidance response combining domain knowledge and Socratic guidance"""
        
        domain_result = agent_results.get("domain", {})
        socratic_result = agent_results.get("socratic", {})
        
        # Prioritize Socratic guidance for design questions
        if socratic_result and socratic_result.get("response_text"):
            return socratic_result.get("response_text", "")
        
        # Fallback to domain knowledge if available
        if domain_result and domain_result.get("response_text"):
            return domain_result.get("response_text", "")
        
        # Fallback design guidance response
        return "That's a great design question! Let me help you think through this systematically. What specific aspects of your design are you trying to optimize?"

    def _extract_building_type_from_context(self, state: ArchMentorState) -> str:
        """Extract building type from context"""
        try:
            # Try to get from analysis result
            if hasattr(state, 'analysis_result') and state.analysis_result:
                analysis_result = state.analysis_result
                if isinstance(analysis_result, dict):
                    text_analysis = analysis_result.get('text_analysis', {})
                    building_type = text_analysis.get('building_type', 'project')
                    return building_type if building_type != 'unknown' else 'project'
            
            # Try to get from current design brief
            if hasattr(state, 'current_design_brief') and state.current_design_brief:
                brief_lower = state.current_design_brief.lower()
                building_types = ['residential', 'commercial', 'educational', 'healthcare', 'cultural', 'office', 'retail']
                for btype in building_types:
                    if btype in brief_lower:
                        return btype
            
            return 'project'
        except:
            return 'project'
    
    def _extract_topic_from_user_input(self, user_input: str) -> str:
        """Extract main topic from user input"""
        # Simple topic extraction
        topics = ['circulation', 'lighting', 'spatial', 'form', 'function', 'context', 'materials', 'structure']
        user_lower = user_input.lower()
        
        for topic in topics:
            if topic in user_lower:
                return topic
        
        return 'design'
    
    async def _add_milestone_question_if_needed(self, state: WorkflowState, final_response: str) -> Optional[str]:
        """Add milestone question if needed based on conversation gaps"""
        
        try:
            # Get current phase from analysis result
            analysis_result = state.get("analysis_result", {})
            phase_analysis = analysis_result.get("phase_analysis", {})
            current_phase = phase_analysis.get("phase", "ideation")
            
            # Get student state
            student_state = state.get("student_state")
            if not student_state:
                return None
            
            # Get progress manager from analysis agent
            if hasattr(self.analysis_agent, 'progress_manager'):
                progress_manager = self.analysis_agent.progress_manager
            else:
                # Create progress manager if not exists
                from phase_management.progress_manager import ProgressManager
                progress_manager = ProgressManager()
                self.analysis_agent.progress_manager = progress_manager
            
            # Generate student ID
            student_id = f"student_{hash(str(student_state.messages))}"
            
            # Check if milestone question is needed
            milestone_question = self.analysis_agent._generate_milestone_question_if_needed(
                student_state, current_phase, progress_manager, student_id
            )
            
            if milestone_question:
                self.logger.info(f"🎯 Adding milestone question: {milestone_question}")
                return milestone_question
            
            return None
            
        except Exception as e:
            self.logger.warning(f"Could not generate milestone question: {e}")
            return None

    def _synthesize_example_response(self, domain_result: Dict, user_input: str, classification: Dict, state: ArchMentorState = None) -> str:
        """Synthesize focused example response with Socratic questions"""
        
        # Get domain expert examples
        domain_text = domain_result.get("response_text", "") if domain_result else ""
        
        # Get Socratic questions about the examples (if available)
        socratic_result = None  # This will be passed from the state in the main synthesis method
        
        # For now, return just the domain expert examples
        # The main synthesis method will handle combining with Socratic questions
        if domain_text:
            return domain_text
        
        # Dynamic fallback - generate contextual response
        building_type = self._extract_building_type_from_context(state)
        topic = self._extract_topic_from_user_input(user_input)
        
        return f"I'd be happy to help you explore {topic} for your {building_type} project! To provide the most relevant guidance, could you tell me what specific aspect of {topic} you're most interested in understanding?"
    
    def _synthesize_feedback_response(self, socratic_result: Dict, domain_result: Dict, user_input: str, classification: Dict) -> str:
        """Synthesize focused feedback response"""
        
        if socratic_result and socratic_result.get("response_text"):
            return socratic_result["response_text"]
        
        if domain_result and domain_result.get("response_text"):
            return domain_result["response_text"]
        
        # Dynamic fallback feedback response
        building_type = 'project'  # Default fallback since we don't have state parameter
        return f"I'd be glad to provide feedback on your {building_type} design! To give you the most useful feedback, could you tell me what specific aspects of your project you'd like me to focus on?"
    
    def _synthesize_technical_response(self, domain_result: Dict, user_input: str, classification: Dict) -> str:
        """Synthesize focused technical response"""
        
        if domain_result and domain_result.get("response_text"):
            return domain_result["response_text"]
        
        # Dynamic fallback technical response
        topic = self._extract_topic_from_user_input(user_input)
        return f"I'd be happy to help with technical requirements for {topic}! Could you specify what technical aspects you need information about?"
    
    def _synthesize_clarification_response(self, socratic_result: Dict, domain_result: Dict, user_input: str, classification: Dict) -> str:
        """Synthesize focused clarification response"""
        
        if socratic_result and socratic_result.get("response_text"):
            return socratic_result["response_text"]
        
        if domain_result and domain_result.get("response_text"):
            return domain_result["response_text"]
        
        # Dynamic fallback clarification response
        topic = self._extract_topic_from_user_input(user_input)
        return f"I understand {topic} can be complex! Let me help clarify. What specific part would you like me to explain in more detail?"
    
    def _synthesize_improvement_response(self, socratic_result: Dict, domain_result: Dict, user_input: str, classification: Dict) -> str:
        """Synthesize focused improvement response"""
        
        if domain_result and domain_result.get("response_text"):
            return domain_result["response_text"]
        
        if socratic_result and socratic_result.get("response_text"):
            return socratic_result["response_text"]
        
        # Dynamic fallback improvement response
        topic = self._extract_topic_from_user_input(user_input)
        return f"Great question about improving your {topic}! What specific aspects would you like to enhance? This will help me suggest the most effective improvements."
    
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
    
    def _synthesize_exploratory_response(self, socratic_result: Dict, domain_result: Dict, user_input: str, classification: Dict) -> str:
        """Synthesize focused exploratory response for open-ended exploration"""
        
        if socratic_result and socratic_result.get("response_text"):
            return socratic_result["response_text"]
        
        if domain_result and domain_result.get("response_text"):
            return domain_result["response_text"]
        
        # Fallback exploratory response
        topic = self._extract_topic_from_user_input(user_input)
        return f"That's an interesting direction to explore with {topic}! Let's think about this together. What aspects of {topic} are most important to your project goals?"
        
    # MAIN EXECUTION METHOD
    async def process_student_input(self, student_state: ArchMentorState) -> Dict[str, Any]:
        """Main method to process student input through the full workflow"""

        import time
        start_time = time.time()
        
        self.logger.info("🚀 LangGraph Orchestrator: Starting workflow...")

        # Ensure the brief is the first message if starting a new project
        if student_state.ensure_brief_in_messages():
            # Check if the brief is already in the messages
            if not any(msg.get("role") == "brief" for msg in student_state.messages):
                # Insert the brief as the first message
                student_state.messages.insert(0, {
                    "role": "brief",
                    "content": student_state.current_design_brief
                })

        # Get the current user input from the last message or from the state
        # The user input should be the last message in the state
        user_messages = [msg for msg in student_state.messages if msg.get('role') == 'user']
        current_user_input = user_messages[-1]['content'] if user_messages else ""
        
        self.logger.info(f"📝 Processing user input: {current_user_input[:100]}...")

        # MILESTONE-DRIVEN CONVERSATION PROGRESSION
        # Update conversation progression manager with current state
        self.progression_manager.update_state(student_state)
        
        # Get milestone guidance for current conversation state
        milestone_guidance = self.progression_manager.get_milestone_driven_agent_guidance(current_user_input, student_state)
        current_milestone = milestone_guidance.get("current_milestone")
        agent_focus = milestone_guidance.get("agent_focus", "context_agent")
        agent_guidance = milestone_guidance.get("agent_guidance", {})
        
        self.logger.info(f"🎯 Current milestone: {current_milestone.milestone_type.value if current_milestone else 'None'}")
        self.logger.info(f"🎯 Agent focus: {agent_focus}")
        self.logger.info(f"🎯 Milestone progress: {milestone_guidance.get('milestone_progress', 0)}%")

        # Check if this is the first message (new conversation)
        if len(user_messages) == 1:
            # Analyze first message for conversation progression
            progression_analysis = self.progression_manager.analyze_first_message(current_user_input, student_state)
            self.logger.info(f"🎯 First message analysis: {progression_analysis.get('conversation_phase', 'unknown')}")
        else:
            # Progress the conversation and assess milestone completion
            last_assistant_message = ""
            for msg in reversed(student_state.messages):
                if msg.get('role') == 'assistant':
                    last_assistant_message = msg.get('content', '')
                    break
            
            # 0708-Assess milestone completion
            milestone_assessment = self.progression_manager.assess_milestone_completion(
                current_user_input, last_assistant_message, student_state
            )
            
            if milestone_assessment.get("milestone_complete", False):
                self.logger.info(f"✅ Milestone completed: {current_milestone.milestone_type.value if current_milestone else 'None'}")
                if milestone_assessment.get("phase_transition", False):
                    self.logger.info(f"🔄 Phase transition to: {milestone_assessment.get('next_phase', 'unknown')}")
            
            progression_analysis = self.progression_manager.progress_conversation(
                current_user_input, last_assistant_message, student_state
            )
            self.logger.info(f"🔄 Conversation progression: {progression_analysis.get('conversation_phase', 'unknown')}")

        # Initialize workflow state with milestone guidance
        initial_state = WorkflowState(
            student_state=student_state,
            last_message=current_user_input,
            student_classification={},
            context_analysis={},
            routing_decision={},
            analysis_result={},
            domain_expert_result={},
            socratic_result={},
            cognitive_enhancement_result={},
            final_response="",
            response_metadata={},
            # Add conversation progression and milestone data
            conversation_progression=progression_analysis,
            milestone_guidance=milestone_guidance
        )

        # Execute the workflow
        final_state = await self.workflow.ainvoke(initial_state)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Add processing time to metadata
        if "response_metadata" in final_state:
            final_state["response_metadata"]["processing_time"] = f"{processing_time:.2f}s"
            # Add conversation progression and milestone data to metadata
            final_state["response_metadata"]["conversation_progression"] = progression_analysis
            final_state["response_metadata"]["milestone_guidance"] = milestone_guidance

        self.logger.info("✅ LangGraph workflow completed!")
        
        # Print the specific information requested by user
        self._print_user_requested_info(final_state)

        return {
            "response": final_state["final_response"],
            "metadata": final_state["response_metadata"],
            "routing_path": final_state["routing_decision"].get("path", "unknown"),
            "classification": final_state["student_classification"],
            "conversation_progression": progression_analysis,
            "milestone_guidance": milestone_guidance
        }
    
    def _detect_topic_transition(self, student_state: ArchMentorState, current_message: str) -> Optional[str]:
        """Detect if user is transitioning to a new topic"""
        
        # Get recent conversation context
        recent_messages = student_state.messages[-3:] if len(student_state.messages) >= 3 else student_state.messages
        
        # Extract topics from recent messages
        recent_topics = []
        for msg in recent_messages:
            if msg.get('role') == 'user':
                topics = self._extract_topics_from_message(msg['content'])
                recent_topics.extend(topics)
        
        # Extract topics from current message
        current_topics = self._extract_topics_from_message(current_message)
        
        # Check for new topics not in recent conversation
        new_topics = [topic for topic in current_topics if topic not in recent_topics]
        
        # Topic transition indicators
        transition_indicators = [
            "what about", "how about", "let's talk about", "i want to discuss",
            "can we explore", "i'm interested in", "tell me about", "what if",
            "another thing", "different topic", "switch to", "move on to"
        ]
        
        has_transition_indicator = any(indicator in current_message.lower() for indicator in transition_indicators)
        
        # Return the first new topic if detected
        if new_topics and (has_transition_indicator or len(new_topics) > 1):
            return new_topics[0]
        
        return None
    
    def _extract_topics_from_message(self, message: str) -> List[str]:
        """Extract architectural topics from a message"""
        
        topics = []
        message_lower = message.lower()
        
        topic_keywords = {
            "residential": ["house", "home", "apartment", "residential", "living", "dwelling"],
            "commercial": ["office", "commercial", "retail", "business", "workplace", "corporate"],
            "cultural": ["museum", "theater", "gallery", "cultural", "arts", "performance"],
            "educational": ["school", "university", "education", "learning", "classroom", "academic"],
            "healthcare": ["hospital", "clinic", "healthcare", "medical", "health"],
            "sustainability": ["sustainable", "green", "environmental", "eco", "climate"],
            "urban": ["urban", "city", "public", "street", "neighborhood", "public space"],
            "interior": ["interior", "furniture", "furnishing", "decoration", "inside"],
            "structure": ["structure", "construction", "building", "system", "engineering"],
            "design_process": ["design", "process", "methodology", "approach", "thinking"]
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                topics.append(topic)
        
        return topics    
    
# Test the LangGraph orchestrator
async def test_langgraph_orchestrator():
    logger = logging.getLogger(__name__)
    logger.info("🧪 Testing LangGraph Orchestrator...")
    
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
        logger.info(f"\n📝 Test {i+1}: {test_case['input']}")
        
        # Create test state
        from state_manager import ArchMentorState, StudentProfile
        state = ArchMentorState()
        state.current_design_brief = "Design a community center for 200 people"
        state.student_profile = StudentProfile(skill_level="intermediate")
        state.messages.append({"role": "user", "content": test_case["input"]})
        
        # Process through LangGraph
        result = await orchestrator.process_student_input(state)
        
        logger.info(f"   Expected Path: {test_case['expected_path']}")
        logger.info(f"   Actual Path: {result['routing_path']}")
        logger.info(f"   Response Type: {result['metadata'].get('response_type', 'N/A')}")
        logger.info(f"   Response: {result['response'][:100]}...")

        
        # Check if routing matches expectation
        if result['routing_path'] == test_case['expected_path']:
            logger.info("   ✅ Routing correct!")
        else:
            logger.warning("   ⚠️ Routing different than expected")

if __name__ == "__main__":
    asyncio.run(test_langgraph_orchestrator())
