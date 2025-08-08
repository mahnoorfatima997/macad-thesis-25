import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'thesis-agents'))

from agents.context_agent import ContextAgent
from state_manager import ArchMentorState, StudentProfile

async def test_manual_override_flexibility():
    """Test how the manual override system handles different user expressions"""
    
    # Initialize context agent
    context_agent = ContextAgent()
    
    # Create a basic state
    state = ArchMentorState(
        student_profile=StudentProfile(
            skill_level="beginner",
            learning_style="visual"
        ),
        messages=[
            {"role": "assistant", "content": "What type of building would you like to design?"},
            {"role": "user", "content": "I want to design a community center"}
        ]
    )
    
    # Test cases with different ways to express the same intent
    test_cases = [
        # Example Request - Different ways to ask for examples
        ("show me examples", "example_request"),
        ("can you give me examples", "example_request"),
        ("I'd like to see some examples", "example_request"),
        ("provide me with examples", "example_request"),
        ("I want to see case studies", "example_request"),
        ("can you show me precedents", "example_request"),
        ("I need some references", "example_request"),
        ("give me some examples", "example_request"),
        
        # Knowledge Request - Different ways to ask for information
        ("tell me about", "knowledge_request"),
        ("what are", "knowledge_request"),
        ("explain", "knowledge_request"),
        ("describe", "knowledge_request"),
        ("I want to learn about", "knowledge_request"),
        ("can you explain", "knowledge_request"),
        ("I need to understand", "knowledge_request"),
        ("what is", "knowledge_request"),
        
        # Direct Answer Request (Cognitive Offloading) - Different ways to ask for complete solutions
        ("can you design", "direct_answer_request"),
        ("design this for me", "direct_answer_request"),
        ("do it for me", "direct_answer_request"),
        ("show me exactly", "direct_answer_request"),
        ("tell me exactly", "direct_answer_request"),
        ("give me the answer", "direct_answer_request"),
        ("just tell me", "direct_answer_request"),
        ("what's the solution", "direct_answer_request"),
        ("make it for me", "direct_answer_request"),
        ("complete design", "direct_answer_request"),
        ("full design", "direct_answer_request"),
        ("finished design", "direct_answer_request"),
        ("what should I design", "direct_answer_request"),
        ("design it for me", "direct_answer_request"),
        
        # Variations that might NOT be caught by manual override
        ("I need you to create", "AI classification"),
        ("Could you build", "AI classification"),
        ("I'd like to see some", "AI classification"),
        ("Can I get references", "AI classification"),
        ("I want you to make", "AI classification"),
        ("Please design", "AI classification"),
        ("I need a complete", "AI classification"),
        ("Show me how to", "AI classification"),
    ]
    
    print("🧪 TESTING MANUAL OVERRIDE FLEXIBILITY")
    print("=" * 60)
    
    for i, (user_input, expected_type) in enumerate(test_cases, 1):
        print(f"\n{i:2d}. User Input: '{user_input}'")
        print(f"    Expected: {expected_type}")
        
        try:
            # Get manual classification first
            manual_type = context_agent._classify_interaction_type(user_input, state)
            
            # Get full classification
            full_classification = await context_agent._perform_core_classification(user_input, state)
            actual_type = full_classification.get("interaction_type", "unknown")
            manual_override = full_classification.get("manual_override", False)
            
            print(f"    Manual Type: {manual_type}")
            print(f"    Final Type: {actual_type}")
            print(f"    Manual Override: {manual_override}")
            
            # Determine if this was handled by manual override or AI
            if manual_override:
                print(f"    ✅ MANUAL OVERRIDE: Pattern-based classification")
            else:
                print(f"    🤖 AI CLASSIFICATION: LLM handled variation")
                
            # Check if the result matches expectation
            if expected_type == "AI classification":
                if not manual_override:
                    print(f"    ✅ CORRECT: AI handled variation as expected")
                else:
                    print(f"    ⚠️  UNEXPECTED: Manual override caught this")
            else:
                if actual_type == expected_type:
                    print(f"    ✅ CORRECT: Matched expected type")
                else:
                    print(f"    ❌ MISMATCH: Expected {expected_type}, got {actual_type}")
                    
        except Exception as e:
            print(f"    ❌ ERROR: {e}")
    
    print("\n" + "=" * 60)
    print("📊 SUMMARY:")
    print("- Manual override catches specific, unambiguous patterns")
    print("- AI classification handles variations and context")
    print("- This hybrid approach balances precision with flexibility")

if __name__ == "__main__":
    asyncio.run(test_manual_override_flexibility()) 