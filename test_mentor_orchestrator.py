"""
Test MENTOR orchestrator integration
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

async def test_orchestrator():
    """Test the orchestrator with a simple input"""
    print("Testing MENTOR Orchestrator Integration...")
    print("=" * 50)
    
    try:
        # Initialize orchestrator
        orchestrator = LangGraphOrchestrator(domain="architecture")
        print("✓ Orchestrator initialized")
        
        # Create test state
        state = ArchMentorState(
            messages=[{
                "role": "user",
                "content": "I want to design a community center that brings people together"
            }],
            current_design_brief="Design a community center for 15,000 residents",
            student_profile=StudentProfile(
                skill_level="intermediate",
                learning_style="visual"
            )
        )
        print("✓ State created")
        
        # Process input
        print("\nProcessing user input...")
        result = await orchestrator.process_student_input(state)
        
        print("\n✓ Result received:")
        print(f"Response: {result.get('response', 'No response')[:200]}...")
        print(f"Routing Path: {result.get('routing_path', 'Unknown')}")
        print(f"Metadata: {result.get('metadata', {})}")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_orchestrator())
    if success:
        print("\n✅ MENTOR orchestrator is working correctly!")
    else:
        print("\n❌ MENTOR orchestrator has issues")