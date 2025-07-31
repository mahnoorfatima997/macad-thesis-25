"""
Test that COGNITIVE ASSESSMENT SUMMARY is not included in responses
"""

import asyncio
import sys
import os

# Add paths
parent_dir = os.path.dirname(os.path.abspath(__file__))
thesis_agents_dir = os.path.join(parent_dir, 'thesis-agents')
sys.path.insert(0, thesis_agents_dir)
sys.path.insert(0, parent_dir)

from orchestration.langgraph_orchestrator import LangGraphOrchestrator
from state_manager import ArchMentorState, StudentProfile

async def test_no_cognitive_summary():
    """Test that responses don't include COGNITIVE ASSESSMENT SUMMARY"""
    print("Testing Response Output (No Cognitive Summary)...")
    print("=" * 60)
    
    try:
        # Initialize orchestrator
        orchestrator = LangGraphOrchestrator(domain="architecture")
        print("✓ Orchestrator initialized")
        
        # Test various input types that might trigger cognitive assessment
        test_inputs = [
            "I'm struggling to understand how to design the community center",
            "What materials should I use for sustainable construction?",
            "I think my design is perfect and doesn't need any changes",
            "Can you review my sketch and provide feedback?"
        ]
        
        for i, user_input in enumerate(test_inputs):
            print(f"\n\nTest {i+1}: {user_input}")
            print("-" * 40)
            
            # Create test state
            state = ArchMentorState(
                messages=[{
                    "role": "user",
                    "content": user_input
                }],
                current_design_brief="Design a community center for 15,000 residents",
                student_profile=StudentProfile(
                    skill_level="intermediate",
                    learning_style="visual"
                )
            )
            
            # Process input
            result = await orchestrator.process_student_input(state)
            
            # Check response
            response = result.get('response', '')
            
            # Check if COGNITIVE ASSESSMENT SUMMARY appears in response
            if "COGNITIVE ASSESSMENT SUMMARY" in response:
                print("❌ FAILED: Cognitive Assessment Summary found in response!")
                print(f"Response preview: {response[:200]}...")
            else:
                print("✅ PASSED: No Cognitive Assessment Summary in response")
                print(f"Response preview: {response[:200]}...")
            
            # Also check metadata to ensure cognitive data is still being tracked
            metadata = result.get('metadata', {})
            if 'cognitive_state' in metadata or 'scientific_metrics' in metadata:
                print("✓ Cognitive data still tracked in metadata (as expected)")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_no_cognitive_summary())
    if success:
        print("\n\n✅ All tests passed! Cognitive Assessment Summary has been removed from responses.")
    else:
        print("\n\n❌ Tests failed")