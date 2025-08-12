#!/usr/bin/env python3
"""
Test script to check what the system returns for museum circulation questions.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the thesis-agents directory to the path
sys.path.append('thesis-agents')

async def test_museum_circulation():
    """Test the system with a museum circulation question."""
    
    print("🧪 Testing Museum Circulation Question")
    print("=" * 50)
    
    # Test question
    test_question = "museums that has interesting circulation approach"
    print(f"Question: {test_question}")
    print()
    
    try:
        # Import the necessary components
        from agents.domain_expert.adapter import DomainExpertAgent
        from state_manager import ArchMentorState
        
        # Create a mock state
        state = ArchMentorState(
            messages=[
                {"role": "user", "content": test_question}
            ],
            current_design_brief="museum design project",
            building_type="cultural"
        )
        
        # Create context classification
        context_classification = {
            "interaction_type": "example_request",
            "user_input": test_question,
            "understanding_level": "intermediate",
            "confidence_level": "confident",
            "engagement_level": "high",
            "primary_gap": "design_examples"
        }
        
        # Create analysis result
        analysis_result = {
            "cognitive_state": {"primary_gap": "design_examples"},
            "text_analysis": {"building_type": "cultural"}
        }
        
        # Create routing decision
        routing_decision = {
            "route": "knowledge_only",
            "path": "knowledge_only"
        }
        
        print("🏗️  Creating Domain Expert Agent...")
        
        # Create the domain expert agent
        agent = DomainExpertAgent()
        
        print("📚 Calling provide_knowledge...")
        
        # Call the provide_knowledge method
        response = await agent.provide_knowledge(
            state, 
            context_classification, 
            analysis_result, 
            routing_decision
        )
        
        print("✅ Response received!")
        print()
        print("📋 Response Details:")
        print(f"Type: {type(response)}")
        print(f"Response Type: {getattr(response, 'response_type', 'unknown')}")
        print()
        
        if hasattr(response, 'response_text'):
            print("📝 Response Text:")
            print("-" * 30)
            print(response.response_text)
            print("-" * 30)
        else:
            print("❌ No response_text attribute found")
            print(f"Available attributes: {dir(response)}")
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_museum_circulation())
