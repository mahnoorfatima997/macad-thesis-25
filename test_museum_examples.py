#!/usr/bin/env python3
"""
Test script to check the example search functionality for museums.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the thesis-agents directory to the path
sys.path.append('thesis-agents')

async def test_museum_examples():
    """Test the example search functionality for museums."""
    
    print("🧪 Testing Museum Example Search")
    print("=" * 50)
    
    # Test question that SHOULD trigger example search
    test_question = "can you provide examples of museums with interesting circulation approaches?"
    print(f"Question: {test_question}")
    print()
    
    try:
        # Import the necessary components
        from agents.domain_expert.adapter import DomainExpertAgent
        from state_manager import ArchMentorState
        
        # Create a mock state with more messages to pass cognitive offloading protection
        state = ArchMentorState(
            messages=[
                {"role": "user", "content": "I'm designing a museum"},
                {"role": "assistant", "content": "That sounds interesting! What type of museum?"},
                {"role": "user", "content": "A contemporary art museum"},
                {"role": "assistant", "content": "Great choice! Contemporary art museums have unique challenges."},
                {"role": "user", "content": "I want to focus on circulation"},
                {"role": "assistant", "content": "Circulation is crucial for museums. How do you envision the flow?"},
                {"role": "user", "content": "I'm thinking about visitor experience"},
                {"role": "assistant", "content": "Visitor experience is key. What specific aspects concern you?"},
                {"role": "user", "content": "I need to understand different approaches"},
                {"role": "assistant", "content": "That's a good approach. Let's explore the options."},
                {"role": "user", "content": test_question}  # This is the 11th user message
            ],
            current_design_brief="museum design project with focus on circulation",
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
    asyncio.run(test_museum_examples())
