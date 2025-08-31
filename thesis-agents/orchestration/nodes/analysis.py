from typing import Callable

from orchestration.types import WorkflowState


def make_analysis_node(analysis_agent, state_validator, state_monitor, logger, progression_manager) -> Callable[[WorkflowState], WorkflowState]:
    async def handler(state: WorkflowState) -> WorkflowState:
        validation_result = state_validator.validate_state(state["student_state"])
        if not validation_result.is_valid:
            logger.warning(f"State validation failed in analysis_agent_node: {validation_result.errors}")

        state_monitor.record_state_change(state["student_state"], "analysis_agent_node_input")

        student_state = state["student_state"]
        context_package = state.get("context_package", {})
        last_message = state.get("last_message", "")

        progression_integration = analysis_agent.integrate_conversation_progression(student_state, last_message, "")
        analysis_result = await analysis_agent.process(student_state, context_package)

        # Ensure analysis_result is a dictionary, not an AgentResponse object
        if hasattr(analysis_result, 'to_dict'):
            try:
                analysis_result = analysis_result.to_dict()
            except Exception as e:
                logger.error(f"Failed to convert AgentResponse to dict: {e}")
                # Fallback: create a basic dictionary
                analysis_result = {
                    "response_text": str(analysis_result),
                    "response_type": "error",
                    "error_message": f"Conversion failed: {e}"
                }
        elif not isinstance(analysis_result, dict):
            # If it's not a dict and doesn't have to_dict, convert to string
            analysis_result = {
                "response_text": str(analysis_result),
                "response_type": "unknown",
                "error_message": "Result was not an AgentResponse or dict"
            }

        # ENHANCED: Add visual analysis if visual artifacts are present
        if hasattr(student_state, 'current_sketch') and student_state.current_sketch:
            logger.info("Processing visual analysis in analysis node...")
            try:
                # Extract visual analysis from the current sketch if available
                if hasattr(student_state.current_sketch, 'analysis_data') and student_state.current_sketch.analysis_data:
                    visual_data = student_state.current_sketch.analysis_data

                    # Convert comprehensive vision analysis to format expected by agents
                    visual_analysis = {
                        "design_strengths": visual_data.get('key_insights', {}).get('strengths', []) if isinstance(visual_data.get('key_insights'), dict) else [],
                        "improvement_opportunities": visual_data.get('key_insights', {}).get('opportunities', []) if isinstance(visual_data.get('key_insights'), dict) else [],
                        "identified_elements": visual_data.get('key_insights', {}).get('elements', []) if isinstance(visual_data.get('key_insights'), dict) else [],
                        "description": visual_data.get('detailed_analysis', ''),
                        "confidence": visual_data.get('confidence', 0.5),
                        "drawing_type": visual_data.get('drawing_type', 'architectural drawing')
                    }

                    analysis_result["visual_analysis"] = visual_analysis
                    logger.info(f"Visual analysis integrated: {visual_analysis.get('drawing_type', 'unknown type')}")
                else:
                    logger.warning("Visual artifact present but no analysis data found")
            except Exception as ve:
                logger.error(f"Error processing visual analysis: {ve}")

        # 1108 tracking: Phase detection (real tracking): compute early and attach to analysis_result
        try:
            from phase_assessment.phase_manager import PhaseAssessmentManager
            phase_manager = PhaseAssessmentManager()
            current_phase, current_step = phase_manager.detect_current_phase(student_state)

            step_progress_map = {
                "initial_context_reasoning": 0.25,
                "knowledge_synthesis_trigger": 0.5,
                "socratic_questioning": 0.75,
                "metacognitive_prompt": 1.0,
            }
            prog = step_progress_map.get(getattr(current_step, 'value', ''), 0.25)
            user_msg_count = len([m for m in getattr(student_state, 'messages', []) if m.get('role') == 'user'])
            confidence = max(0.5, min(0.95, 0.5 + (user_msg_count / 20.0) + (prog - 0.25) / 2))

            analysis_result["phase_analysis"] = {
                "phase": current_phase.value,
                "step": current_step.value,
                "confidence": confidence,
                "progression_score": prog,
                # back-compat keys
                "current_phase": current_phase.value,
                "current_step": current_step.value,
                "phase_confidence": confidence,
            }
        except Exception:
            pass

        analysis_result.update({
            "conversation_progression": progression_integration.get("conversation_progression", {}),
            "current_milestone": progression_integration.get("current_milestone"),
            "milestone_assessment": progression_integration.get("milestone_assessment", {}),
            "agent_guidance": progression_integration.get("agent_guidance", {}),
        })

        result_state = {
            **state,
            "analysis_result": analysis_result,
            "conversation_progression": progression_integration.get("conversation_progression", {}),
            "milestone_guidance": progression_integration.get("agent_guidance", {}),
        }

        output_validation = state_validator.validate_state(result_state["student_state"])
        if not output_validation.is_valid:
            logger.warning(f"Output state validation failed in analysis_agent_node: {output_validation.errors}")

        state_monitor.record_state_change(result_state["student_state"], "analysis_agent_node_output")
        return result_state

    return handler


