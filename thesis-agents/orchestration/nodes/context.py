from typing import Callable, Dict, Any

from ..types import WorkflowState


def make_context_node(context_agent, progression_manager, first_response_generator, state_validator, state_monitor, logger) -> Callable[[WorkflowState], Any]:
    async def handler(state: WorkflowState) -> WorkflowState:
        # Reuse original logic by delegating to the context_agent
        # The original orchestrator also handled "first message" logic; keep parity here.

        # Validate input
        validation_result = state_validator.validate_state(state["student_state"])
        if not validation_result.is_valid:
            logger.warning(f"State validation failed in context_agent_node: {validation_result.errors}")

        state_monitor.record_state_change(state["student_state"], "context_agent_node_input")

        student_state = state["student_state"]
        last_message = state["last_message"]

        # Detect first-message progressive path using improved heuristic
        user_messages = [m["content"] for m in student_state.messages if m.get("role") == "user"]
        assistant_messages = [m for m in student_state.messages if m.get("role") == "assistant"]
        
        logger.info(f"Context node: user_messages count: {len(user_messages)}, assistant_messages count: {len(assistant_messages)}")
        logger.info(f"Context node: last_message: {last_message[:100]}...")
        
        # Check if this is the EXACT moment for progressive opening
        # CRITICAL: Progressive opening triggers ONLY when:
        # - Exactly 2 user messages (brief + first real message)
        # - Zero assistant messages (no previous responses)
        # - No image upload in the conversation
        # This ensures it triggers only ONCE per conversation at the right moment
        has_image_upload = any(
            m.get("has_uploaded_image", False) or "image" in m.get("content", "").lower()
            for m in student_state.messages
        )

        is_first_message = (
            len(user_messages) == 2 and
            len(assistant_messages) == 0 and
            not has_image_upload
        )
        
        # CRITICAL: Progressive opening only triggers at the exact right moment
        if not is_first_message:
            logger.info(f"Context node: Progressive opening will NOT trigger - conditions not met (user_messages: {len(user_messages)}, assistant_messages: {len(assistant_messages)}, has_image: {has_image_upload})")
        
        # 1208-If still not first message, try to get input classification to see if it's a project description
        if not is_first_message and last_message:
            try:
                # FIXED: Use absolute import to avoid relative import warning
                import sys
                import os
                sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
                from agents.context_agent.processors.input_classification import InputClassificationProcessor
                classifier = InputClassificationProcessor()
                # Create a minimal state for classification
                temp_state = type('TempState', (), {'messages': []})()
                classification = await classifier.perform_core_classification(last_message, temp_state)
                if hasattr(classification, 'interaction_type') and classification.interaction_type == 'project_description':
                    is_first_message = True
                    logger.info("Context node: Input classification detected project_description, treating as first message")
            except Exception as e:
                # FIXED: Reduced warning verbosity - this is not critical
                logger.debug(f"Context node: Input classification check skipped: {e}")
        
        logger.info(f"Context node: is_first_message determined as: {is_first_message} (user_messages: {len(user_messages)}, assistant_messages: {len(assistant_messages)}, has_image: {has_image_upload})")

        if is_first_message:
            first_response_result = await first_response_generator.generate_first_response(last_message, student_state)
            progression_analysis = first_response_result.get("progression_analysis", {})
            building_type = first_response_result.get("metadata", {}).get("building_type", "unknown")
            
            # Update the student state with the detected building type
            if building_type != "unknown":
                student_state.building_type = building_type
                print(f"🔍 DEBUG: Updated student_state.building_type to: {student_state.building_type}")
            
            # CRITICAL FIX: Add routing information to response metadata
            response_metadata = first_response_result.get("metadata", {})
            response_metadata.update({
                "routing_path": "progressive_opening",
                "response_type": "progressive_opening",
                "ai_reasoning": f"First message - using progressive conversation system for {building_type} project",
                "interaction_type": "first_message",
                "user_intent": "first_message",
                "agents_used": ["context_agent", "first_response_generator"],
            })

            result_state: WorkflowState = {
                **state,
                "student_state": student_state,  # Ensure the updated state is referenced
                "last_message": last_message,
                "student_classification": {
                    "interaction_type": "first_message",
                    "understanding_level": progression_analysis.get("user_profile", {}).get("knowledge_level", "unknown"),
                    "confidence_level": "neutral",
                    "engagement_level": "medium",
                    "is_first_message": True,
                    "building_type": building_type,
                },
                "context_analysis": {
                    "progression_analysis": progression_analysis,
                    "opening_strategy": first_response_result.get("opening_strategy", {}),
                    "conversation_phase": "discovery",
                    "building_type": building_type,
                },
                "routing_decision": {
                    "path": "progressive_opening",
                    "reasoning": f"First message - using progressive conversation system for {building_type} project",
                },
                "final_response": first_response_result.get("response_text", ""),
                "response_metadata": response_metadata,
                "progression_data": progression_analysis,
            }

            output_validation = state_validator.validate_state(result_state["student_state"])
            if not output_validation.is_valid:
                logger.warning(f"Output state validation failed in context_agent_node: {output_validation.errors}")
            state_monitor.record_state_change(result_state["student_state"], "context_agent_node_output")
            return result_state

        # Ongoing conversation → use context agent comprehensive analysis
        agent_response = await context_agent.analyze_student_input(student_state, last_message)

        # Extract data from AgentResponse
        if hasattr(agent_response, "metadata") and agent_response.metadata:
            # The ContextPackage is stored in the metadata field of AgentResponse
            context_package_data = agent_response.metadata
            core_classification = context_package_data.get("core_classification", {})
            contextual_metadata = context_package_data.get("contextual_metadata", {})
            conversation_patterns = context_package_data.get("conversation_patterns", {})
            routing_suggestions = context_package_data.get("routing_suggestions", {})
            agent_contexts = context_package_data.get("agent_contexts", {})
            context_package = context_package_data
        elif hasattr(agent_response, "to_dict"):
            # Fallback: convert AgentResponse to dict
            agent_response_dict = agent_response.to_dict()
            context_package_data = agent_response_dict.get("metadata", {})
            core_classification = context_package_data.get("core_classification", {})
            contextual_metadata = context_package_data.get("contextual_metadata", {})
            conversation_patterns = context_package_data.get("conversation_patterns", {})
            routing_suggestions = context_package_data.get("routing_suggestions", {})
            agent_contexts = context_package_data.get("agent_contexts", {})
            context_package = context_package_data
        else:
            # Final fallback
            core_classification = {}
            contextual_metadata = {}
            conversation_patterns = {}
            routing_suggestions = {}
            agent_contexts = {}
            context_package = {}

        # Convert CoreClassification object to dictionary for student_classification
        classification_dict = {}

        if isinstance(core_classification, dict):
            classification_dict = core_classification.copy()
        elif hasattr(core_classification, '__dict__'):
            classification_dict = core_classification.__dict__.copy()
        else:
            # Fallback: extract key attributes
            classification_dict = {
                "interaction_type": getattr(core_classification, 'interaction_type', 'unknown'),
                "understanding_level": getattr(core_classification, 'understanding_level', 'medium'),
                "confidence_level": getattr(core_classification, 'confidence_level', 'confident'),
                "engagement_level": getattr(core_classification, 'engagement_level', 'medium'),
            }

        result_state = {
            **state,
            "last_message": last_message,
            "student_classification": {**classification_dict, "last_message": last_message},
            "context_analysis": {
                **context_package,
                "building_type": student_state.building_type,  # Always include building type
            },
            "context_metadata": contextual_metadata,
            "conversation_patterns": conversation_patterns,
            "routing_suggestions": routing_suggestions,
            "agent_contexts": agent_contexts,
            "context_package": context_package,
        }

        output_validation = state_validator.validate_state(result_state["student_state"])
        if not output_validation.is_valid:
            logger.warning(f"Output state validation failed in context_agent_node: {output_validation.errors}")
        state_monitor.record_state_change(result_state["student_state"], "context_agent_node_output")
        return result_state

    return handler


