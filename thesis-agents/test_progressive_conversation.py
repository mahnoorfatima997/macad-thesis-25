# test_progressive_conversation.py - Test Progressive Conversation System
import asyncio
import logging
import sys
import os

# Add path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from state_manager import ArchMentorState, StudentProfile
from conversation_progression import ConversationProgressionManager, ConversationPhase
from first_response_generator import FirstResponseGenerator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_progressive_conversation():
    """Test the progressive conversation system with various first messages"""
    
    logger.info("🧪 Testing Progressive Conversation System")
    
    # Initialize the system
    progression_manager = ConversationProgressionManager("architecture")
    first_response_generator = FirstResponseGenerator("architecture")
    
    # Test cases with different user intents and knowledge levels
    test_cases = [
        {
            "name": "Beginner seeking knowledge",
            "input": "What is sustainable architecture? I want to learn more about it.",
            "expected_dimensions": ["sustainable", "functional"],
            "expected_approach": "concept_introduction"
        },
        {
            "name": "Intermediate exploring ideas",
            "input": "I'm thinking about designing a community center that focuses on spatial relationships and how people move through spaces. How can I approach this?",
            "expected_dimensions": ["spatial", "functional", "contextual"],
            "expected_approach": "idea_refinement"
        },
        {
            "name": "Advanced seeking feedback",
            "input": "I'm working on a museum design that integrates structural innovation with aesthetic expression. The building needs to respond to its urban context while creating meaningful spatial experiences. What do you think about this approach?",
            "expected_dimensions": ["technical", "aesthetic", "contextual", "spatial"],
            "expected_approach": "critical_dialogue"
        },
        {
            "name": "Confused beginner",
            "input": "I don't understand how to start designing. Everything seems so complicated and I don't know where to begin.",
            "expected_dimensions": ["functional", "spatial"],
            "expected_approach": "step_by_step_scaffolding"
        },
        {
            "name": "Overconfident intermediate",
            "input": "My design is obviously perfect. I've created the best solution possible and there's no way it could be improved.",
            "expected_dimensions": ["functional", "spatial"],
            "expected_approach": "collaborative_problem_solving"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        logger.info(f"\n{'='*60}")
        logger.info(f"📝 Test {i}: {test_case['name']}")
        logger.info(f"Input: {test_case['input']}")
        logger.info(f"{'='*60}")
        
        # Create test state
        state = ArchMentorState()
        state.current_design_brief = "Design an architectural project"
        state.student_profile = StudentProfile(skill_level="intermediate")
        state.messages.append({"role": "user", "content": test_case["input"]})
        
        # Test progression analysis
        logger.info("\n🔍 PROGRESSION ANALYSIS:")
        progression_analysis = progression_manager.analyze_first_message(test_case["input"], state)
        
        # Display analysis results
        user_profile = progression_analysis.get("user_profile", {})
        opening_strategy = progression_analysis.get("opening_strategy", {})
        
        logger.info(f"   Knowledge Level: {user_profile.get('knowledge_level', 'unknown')}")
        logger.info(f"   Learning Style: {user_profile.get('learning_style', 'unknown')}")
        logger.info(f"   Primary Intent: {opening_strategy.get('suggested_approach', 'unknown')}")
        logger.info(f"   Primary Dimension: {opening_strategy.get('primary_dimension', 'unknown')}")
        logger.info(f"   Relevant Dimensions: {progression_analysis.get('relevant_dimensions', [])}")
        
        # Test first response generation
        logger.info("\n🤖 FIRST RESPONSE GENERATION:")
        first_response_result = await first_response_generator.generate_first_response(test_case["input"], state)
        
        response_text = first_response_result.get("response_text", "")
        logger.info(f"   Response Type: {first_response_result.get('response_type', 'unknown')}")
        logger.info(f"   Conversation Phase: {first_response_result.get('conversation_phase', 'unknown')}")
        logger.info(f"   Response Length: {len(response_text)} characters")
        
        # Display the response
        logger.info(f"\n💬 GENERATED RESPONSE:")
        logger.info(f"{response_text}")
        
        # Validate expectations
        logger.info(f"\n✅ VALIDATION:")
        relevant_dimensions = progression_analysis.get("relevant_dimensions", [])
        expected_dimensions = test_case["expected_dimensions"]
        
        # relevant_dimensions are already strings (from d.value conversion in analyze_first_message)
        dimension_match = any(dim in relevant_dimensions for dim in expected_dimensions)
        approach_match = opening_strategy.get("suggested_approach", "") == test_case["expected_approach"]
        
        logger.info(f"   Dimensions Match: {'✅' if dimension_match else '❌'}")
        logger.info(f"   Approach Match: {'✅' if approach_match else '❌'}")
        
        if not dimension_match:
            logger.warning(f"   Expected: {expected_dimensions}, Got: {relevant_dimensions}")
        if not approach_match:
            logger.warning(f"   Expected: {test_case['expected_approach']}, Got: {opening_strategy.get('suggested_approach', 'unknown')}")
    
    logger.info(f"\n{'='*60}")
    logger.info("🎉 Progressive Conversation System Test Complete!")
    logger.info(f"{'='*60}")

async def test_conversation_progression():
    """Test conversation progression through phases"""
    
    logger.info("\n🔄 Testing Conversation Progression Through Phases")
    
    progression_manager = ConversationProgressionManager("architecture")
    
    # Simulate a conversation progression
    conversation_steps = [
        {
            "phase": "DISCOVERY",
            "message": "I want to learn about sustainable architecture",
            "expected_phase": ConversationPhase.DISCOVERY
        },
        {
            "phase": "EXPLORATION", 
            "message": "I understand that sustainability involves environmental, social, and economic factors. Can you show me some examples?",
            "expected_phase": ConversationPhase.EXPLORATION
        },
        {
            "phase": "SYNTHESIS",
            "message": "I see how these different aspects connect. The environmental strategies support the social goals, and the economic benefits make it viable.",
            "expected_phase": ConversationPhase.SYNTHESIS
        },
        {
            "phase": "APPLICATION",
            "message": "I'm applying these principles to my community center design. The building orientation maximizes natural light while creating social spaces.",
            "expected_phase": ConversationPhase.APPLICATION
        },
        {
            "phase": "REFLECTION",
            "message": "Looking back, I've learned that sustainability is about integration, not just adding green features. I feel more confident about my approach.",
            "expected_phase": ConversationPhase.REFLECTION
        }
    ]
    
    state = ArchMentorState()
    
    for i, step in enumerate(conversation_steps, 1):
        logger.info(f"\n📝 Step {i}: {step['phase']}")
        logger.info(f"Message: {step['message']}")
        
        # Simulate a more realistic conversation by adding multiple messages
        # Add the current user message
        state.messages.append({"role": "user", "content": step['message']})
        
        # Add some assistant responses to simulate conversation depth
        if i > 1:
            # Add 2-3 assistant responses to simulate conversation progression
            for j in range(2):
                state.messages.append({
                    "role": "assistant", 
                    "content": f"Assistant response {j+1} for step {i-1}"
                })
        
        # Analyze progression
        if i == 1:
            # First message
            progression_analysis = progression_manager.analyze_first_message(step['message'], state)
            current_phase = ConversationPhase.DISCOVERY
        else:
            # Progress conversation
            progression_result = progression_manager.progress_conversation(
                step['message'], 
                "Previous response", 
                state
            )
            current_phase = ConversationPhase(progression_result.get("current_phase", "discovery"))
        
        logger.info(f"   Total Messages: {len(state.messages)}")
        logger.info(f"   Current Phase: {current_phase.value}")
        logger.info(f"   Expected Phase: {step['expected_phase'].value}")
        logger.info(f"   Phase Match: {'✅' if current_phase == step['expected_phase'] else '❌'}")
        
        # Show progression guidance
        if hasattr(progression_manager, '_generate_progression_guidance'):
            guidance = progression_manager._generate_progression_guidance({
                "message_count": len(state.messages),
                "understanding_depth": "medium" if i <= 2 else "high",
                "readiness_for_advancement": i > 2
            })
            
            logger.info(f"   Phase Objectives: {guidance.get('phase_objectives', [])[:2]}...")
            logger.info(f"   Suggested Approaches: {guidance.get('suggested_approaches', [])[:2]}...")

async def test_design_space_opening():
    """Test design space opening for different dimensions"""
    
    logger.info("\n🎨 Testing Design Space Opening")
    
    progression_manager = ConversationProgressionManager("architecture")
    
    # Test different design dimensions
    dimensions = [
        "functional",
        "spatial", 
        "technical",
        "contextual",
        "aesthetic",
        "sustainable"
    ]
    
    for dimension in dimensions:
        logger.info(f"\n🏗️ Testing {dimension.upper()} Dimension:")
        
        # Import DesignSpaceDimension enum
        from conversation_progression import DesignSpaceDimension
        
        try:
            dimension_enum = getattr(DesignSpaceDimension, dimension.upper())
            design_space = progression_manager.design_space_map.get(dimension_enum)
            
            if design_space:
                logger.info(f"   Opening Questions: {design_space.opening_questions[:2]}...")
                logger.info(f"   Exploration Prompts: {design_space.exploration_prompts[:2]}...")
                logger.info(f"   Knowledge Gaps: {design_space.knowledge_gaps}")
                logger.info(f"   Complexity Level: {design_space.complexity_level}")
            else:
                logger.warning(f"   No design space found for dimension: {dimension}")
        except AttributeError:
            logger.error(f"   Invalid dimension: {dimension}")
        except Exception as e:
            logger.error(f"   Error testing dimension {dimension}: {e}")

if __name__ == "__main__":
    async def main():
        await test_progressive_conversation()
        await test_conversation_progression()
        await test_design_space_opening()
    
    asyncio.run(main()) 