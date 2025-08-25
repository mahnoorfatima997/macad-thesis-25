#!/usr/bin/env python3
"""
Test mentor conversation continuity and understanding
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Add thesis-agents to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'thesis-agents'))

# Load environment variables
load_dotenv()

def test_mentor_continuity():
    """Test mentor conversation continuity"""
    print("🧪 MENTOR CONVERSATION CONTINUITY TEST")
    print("=" * 60)
    
    try:
        from orchestration.langgraph_orchestrator import LangGraphOrchestrator
        from state_manager import ArchMentorState
        
        # Initialize orchestrator
        orchestrator = LangGraphOrchestrator()
        
        print("✅ Orchestrator initialized successfully")
        
        # Create conversation scenario
        student_state = ArchMentorState()
        student_state.messages = [
            {"role": "user", "content": "I'm designing a community center in a cold climate"},
            {"role": "assistant", "content": "That's an interesting project! Cold climate design requires special considerations for heating, insulation, and creating warm gathering spaces. What specific aspects are you most curious about?"},
            {"role": "user", "content": "looking through someone else's lens is very helpful to consider all user groups with wide range of ages. but I am not sure how to provide a good inner garden strategy for this building. what would be the best idea?"}
        ]
        
        print(f"\n🗣️ Testing conversation continuity...")
        print(f"Previous context: Community center in cold climate")
        print(f"Current message: Inner garden strategy question")
        
        # Test mentor response
        result = asyncio.run(orchestrator.process_student_input(student_state))
        
        print(f"\n📋 MENTOR RESPONSE:")
        print(f"Route: {result.get('routing_path', 'unknown')}")
        print(f"Response: {result.get('response', 'No response')[:200]}...")
        
        # Check if mentor understands context
        response_text = result.get('response', '').lower()
        context_indicators = [
            'community center', 'cold climate', 'inner garden', 
            'user groups', 'ages', 'building'
        ]
        
        context_understood = sum(1 for indicator in context_indicators if indicator in response_text)
        
        print(f"\n🧠 CONTEXT UNDERSTANDING:")
        print(f"Context indicators found: {context_understood}/{len(context_indicators)}")
        
        if context_understood >= 3:
            print("✅ MENTOR UNDERSTANDS CONTEXT")
        else:
            print("❌ MENTOR MISSING CONTEXT")
            
        # Test gamification triggers
        classification = result.get('classification', {})
        print(f"\n🎮 GAMIFICATION CHECK:")
        print(f"User intent: {classification.get('user_intent', 'unknown')}")
        print(f"Route: {result.get('routing_path', 'unknown')}")
        
        if result.get('routing_path') == 'socratic_clarification':
            print("✅ CORRECT ROUTE FOR CONFUSION")
        else:
            print("❌ INCORRECT ROUTE")
            
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_mentor_continuity()
