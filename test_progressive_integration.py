#!/usr/bin/env python3
"""
Test script to verify the progressive conversation system integration
"""

import asyncio
import logging
import sys
import os

# Add the thesis-agents directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'thesis-agents'))

from state_manager import ArchMentorState, StudentProfile, DesignPhase
from conversation_progression import ConversationProgressionManager
from first_response_generator import FirstResponseGenerator

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_progressive_conversation():
    """Test the progressive conversation system directly"""
    
    logger.info("🧪 Testing Progressive Conversation System Integration")
    
    # Test case: Community center design brief
    test_input = """I am designing a community center for a diverse urban neighborhood of 15,000 residents. 
    The site is a former industrial warehouse (150m x 80m x 12m height). 
    I am considering community needs, cultural sensitivity, sustainability, and adaptive reuse principles."""
    
    # Create a fresh student state (simulating first message)
    student_state = ArchMentorState(
        messages=[],  # Empty messages = first message
        current_design_brief=test_input,
        design_phase=DesignPhase.IDEATION,
        visual_artifacts=[],
        current_sketch=None,
        student_profile=StudentProfile(),
        session_metrics={},
        last_agent="",
        next_agent="analysis",
        agent_context={},
        domain="architecture",
        domain_config={},
        show_response_summary=True,
        show_scientific_metrics=False
    )
    
    # Initialize the progressive conversation system
    progression_manager = ConversationProgressionManager("architecture")
    first_response_generator = FirstResponseGenerator("architecture")
    
    logger.info("🎯 Testing First Message Analysis")
    
    # Test the first message analysis
    progression_analysis = progression_manager.analyze_first_message(test_input, student_state)
    
    logger.info(f"📊 Progression Analysis Results:")
    logger.info(f"   - Conversation Phase: {progression_analysis.get('conversation_phase')}")
    logger.info(f"   - Relevant Dimensions: {progression_analysis.get('relevant_dimensions')}")
    logger.info(f"   - User Profile: {progression_analysis.get('user_profile', {}).get('knowledge_level')}")
    
    opening_strategy = progression_analysis.get('opening_strategy', {})
    logger.info(f"   - Opening Strategy: {opening_strategy.get('suggested_approach')}")
    logger.info(f"   - Primary Dimension: {opening_strategy.get('primary_dimension')}")
    
    logger.info("\n🎯 Testing First Response Generation")
    
    # Test the first response generation
    first_response_result = await first_response_generator.generate_first_response(test_input, student_state)
    
    response_text = first_response_result.get("response_text", "")
    logger.info(f"📝 Generated Response Length: {len(response_text)} characters")
    logger.info(f"📝 Response Preview: {response_text[:200]}...")
    
    # Check if the response contains progressive conversation elements
    progressive_elements = [
        "design space",
        "explore",
        "consider",
        "think about",
        "what if",
        "how might",
        "let's examine"
    ]
    
    found_elements = [elem for elem in progressive_elements if elem.lower() in response_text.lower()]
    logger.info(f"🎯 Progressive Elements Found: {found_elements}")
    
    # Test conversation progression
    logger.info("\n🔄 Testing Conversation Progression")
    
    # Simulate a follow-up message
    follow_up_message = "I'd like to focus on adaptive reuse principles to understand how to approach this warehouse conversion."
    
    # Add the first message to state
    student_state.messages.append({"role": "user", "content": test_input})
    student_state.messages.append({"role": "assistant", "content": response_text})
    
    # Test progression
    progression_result = progression_manager.progress_conversation(
        follow_up_message, 
        response_text, 
        student_state
    )
    
    logger.info(f"📊 Progression Results:")
    logger.info(f"   - Current Phase: {progression_result.get('current_phase')}")
    logger.info(f"   - Phase Transition: {progression_result.get('phase_transition')}")
    
    # Test topic transition detection
    logger.info("\n🔄 Testing Topic Transition Detection")
    
    topic_transition_response = first_response_generator.generate_topic_transition_response(
        "adaptive_reuse",
        progression_manager.milestones[-1] if progression_manager.milestones else {},
        student_state
    )
    
    logger.info(f"📝 Topic Transition Response Length: {len(topic_transition_response.get('response_text', ''))}")
    
    logger.info("\n✅ Progressive Conversation System Test Complete!")
    
    return {
        "progression_analysis": progression_analysis,
        "first_response": first_response_result,
        "progression_result": progression_result,
        "topic_transition": topic_transition_response
    }

if __name__ == "__main__":
    asyncio.run(test_progressive_conversation()) 