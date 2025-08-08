import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'thesis-agents'))

from agents.context_agent import ContextAgent
from state_manager import ArchMentorState, StudentProfile

async def test_enhanced_routing_patterns():
    """Test the enhanced routing pattern system to verify fixes"""
    
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
    
    # Test cases that were problematic in the original system
    problematic_test_cases = [
        # These should now be correctly classified
        ("I want to see case studies", "example_request"),
        ("what is", "knowledge_request"),
        ("show me exactly", "direct_answer_request"),
        ("I need you to create", "direct_answer_request"),
        ("Could you build", "direct_answer_request"),
        ("I'd like to see some", "example_request"),
        ("Can I get references", "example_request"),
        ("I want you to make", "direct_answer_request"),
        ("Please design", "direct_answer_request"),
        ("Show me how to", "direct_answer_request"),
        
        # Test pattern disambiguation
        ("show me examples", "example_request"),
        ("show me exactly", "direct_answer_request"),
        ("tell me about", "knowledge_request"),
        ("tell me exactly", "direct_answer_request"),
        ("what is the requirement", "technical_question"),
        ("what is sustainability", "knowledge_request"),
        
        # Test context-dependent patterns
        ("I need to understand", "knowledge_request"),
        ("I want to learn about", "knowledge_request"),
        ("how do I", "implementation_request"),
        ("what steps should I", "implementation_request"),
        ("how to implement", "implementation_request"),
        
        # Test high-confidence patterns
        ("can you design", "direct_answer_request"),
        ("design this for me", "direct_answer_request"),
        ("do it for me", "direct_answer_request"),
        ("make it for me", "direct_answer_request"),
        ("complete design", "direct_answer_request"),
        ("full design", "direct_answer_request"),
        ("finished design", "direct_answer_request"),
        ("design it for me", "direct_answer_request"),
        
        # Test example request patterns
        ("show me examples", "example_request"),
        ("can you give me examples", "example_request"),
        ("provide me with examples", "example_request"),
        ("can you show me precedents", "example_request"),
        ("I need some references", "example_request"),
        ("give me some examples", "example_request"),
        
        # Test knowledge request patterns
        ("tell me about", "knowledge_request"),
        ("what are", "knowledge_request"),
        ("explain", "knowledge_request"),
        ("describe", "knowledge_request"),
        ("I want to learn about", "knowledge_request"),
        ("can you explain", "knowledge_request"),
        
        # Test other interaction types
        ("feedback", "feedback_request"),
        ("review", "feedback_request"),
        ("what do you think", "feedback_request"),
        ("confused", "confusion_expression"),
        ("don't understand", "confusion_expression"),
        ("help", "confusion_expression"),
        ("improve", "improvement_seeking"),
        ("better", "improvement_seeking"),
        ("enhance", "improvement_seeking"),
        ("technical", "technical_question"),
        ("specification", "technical_question"),
        ("requirement", "technical_question"),
    ]
    
    print("🧪 TESTING ENHANCED ROUTING PATTERN SYSTEM")
    print("=" * 60)
    
    success_count = 0
    total_count = len(problematic_test_cases)
    
    for i, (user_input, expected_type) in enumerate(problematic_test_cases, 1):
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
            
            # Check if the result matches expectation
            if actual_type == expected_type:
                print(f"    ✅ CORRECT: Matched expected type")
                success_count += 1
            else:
                print(f"    ❌ MISMATCH: Expected {expected_type}, got {actual_type}")
                
        except Exception as e:
            print(f"    ❌ ERROR: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 RESULTS: {success_count}/{total_count} tests passed ({success_count/total_count*100:.1f}%)")
    
    if success_count == total_count:
        print("🎉 ALL TESTS PASSED! Enhanced routing pattern system is working correctly.")
    else:
        print(f"⚠️  {total_count - success_count} tests failed. Further refinement needed.")
    
    print("\n🔧 ENHANCEMENTS IMPLEMENTED:")
    print("- Level 1: High-Confidence Patterns (Manual Override)")
    print("- Level 2: Context-Dependent Patterns")
    print("- Level 3: Specific Pattern Disambiguation")
    print("- Level 4: Specific Interaction Types")
    print("- Level 5: General Classification")
    print("- Improved pattern specificity and context awareness")

if __name__ == "__main__":
    asyncio.run(test_enhanced_routing_patterns()) 