#!/usr/bin/env python3
"""
Debug script to test the exact message flow in the progressive conversation system
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'thesis-agents'))

from state_manager import ArchMentorState, StudentProfile
from orchestration.langgraph_orchestrator import LangGraphOrchestrator
import asyncio

async def debug_message_flow():
    """Test the exact message flow to understand why progressive conversation isn't working"""
    
    print("🔍 DEBUGGING MESSAGE FLOW")
    print("=" * 50)
    
    # Step 1: Simulate analyze_design behavior
    print("\n📝 STEP 1: Simulating analyze_design behavior")
    design_brief = "I am designing a community center for a diverse urban neighborhood of 15,000 residents. The site is a former industrial warehouse (150m x 80m x 12m height). I am considering community needs, cultural sensitivity, sustainability, and adaptive reuse principles."
    
    state = ArchMentorState()
    state.current_design_brief = design_brief
    state.student_profile = StudentProfile(skill_level="intermediate")
    state.domain = "architecture"
    
    # Add the generic user message that analyze_design adds
    state.messages = [
        {"role": "user", "content": f"I'm working on my {design_brief.lower()[:50]}... and need help with the design process."}
    ]
    
    print(f"After analyze_design:")
    print(f"  - Total messages: {len(state.messages)}")
    print(f"  - Message roles: {[msg.get('role') for msg in state.messages]}")
    print(f"  - User messages: {len([msg for msg in state.messages if msg.get('role') == 'user'])}")
    
    # Step 2: Simulate process_chat_message behavior (user's first interactive input)
    print("\n📝 STEP 2: Simulating process_chat_message behavior")
    user_first_input = "I would like to focus on adaptive reuse principles to know better how to approach turning a former industrial warehouse to a community center"
    
    # Add user's actual input (this happens in process_chat_message)
    state.messages.append({
        "role": "user",
        "content": user_first_input
    })
    
    print(f"After adding user's first interactive input:")
    print(f"  - Total messages: {len(state.messages)}")
    print(f"  - Message roles: {[msg.get('role') for msg in state.messages]}")
    print(f"  - User messages: {len([msg for msg in state.messages if msg.get('role') == 'user'])}")
    
    # Step 3: Simulate process_student_input behavior
    print("\n📝 STEP 3: Simulating process_student_input behavior")
    
    # This is what ensure_brief_in_messages() does
    if state.current_design_brief:
        # Check if brief exists as first message
        brief_exists = (state.messages and
                    state.messages[0].get("role") == "brief" and
                    state.messages[0].get("content") == state.current_design_brief)

        if not brief_exists:
            # Remove any existing brief messages
            state.messages = [msg for msg in state.messages if msg.get("role") != "brief"]
            # Insert current brief at the beginning
            state.messages.insert(0, {
                "role": "brief",
                "content": state.current_design_brief
            })
    
    print(f"After ensure_brief_in_messages:")
    print(f"  - Total messages: {len(state.messages)}")
    print(f"  - Message roles: {[msg.get('role') for msg in state.messages]}")
    print(f"  - User messages: {len([msg for msg in state.messages if msg.get('role') == 'user'])}")
    
    # Step 4: Test the is_first_message logic
    print("\n📝 STEP 4: Testing is_first_message logic")
    
    user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
    last_message = user_first_input  # This would be the current user input
    
    # Current logic in context_agent_node
    is_first_message = len(user_messages) == 0 or (
        len(user_messages) == 2 and 
        state.current_design_brief and
        last_message != state.current_design_brief and
        len([msg for msg in state.messages if msg.get('role') == 'assistant']) == 0
    )
    
    print(f"is_first_message calculation:")
    print(f"  - len(user_messages): {len(user_messages)}")
    print(f"  - len(user_messages) == 2: {len(user_messages) == 2}")
    print(f"  - state.current_design_brief exists: {bool(state.current_design_brief)}")
    print(f"  - last_message != state.current_design_brief: {last_message != state.current_design_brief}")
    print(f"  - No assistant messages: {len([msg for msg in state.messages if msg.get('role') == 'assistant']) == 0}")
    print(f"  - FINAL RESULT: is_first_message = {is_first_message}")
    
    # Step 5: Test with orchestrator
    print("\n📝 STEP 5: Testing with actual orchestrator")
    
    orchestrator = LangGraphOrchestrator("architecture")
    
    # Create the initial state that would be passed to context_agent_node
    from orchestration.langgraph_orchestrator import WorkflowState
    
    initial_state = WorkflowState(
        student_state=state,
        last_message=user_first_input,
        student_classification={},
        context_analysis={},
        routing_decision={},
        analysis_result={},
        domain_expert_result={},
        socratic_result={},
        cognitive_enhancement_result={},
        final_response="",
        response_metadata={}
    )
    
    print(f"Initial state created with:")
    print(f"  - student_state.messages count: {len(initial_state['student_state'].messages)}")
    print(f"  - last_message: {initial_state['last_message'][:50]}...")
    
    # Test the context_agent_node logic directly
    print("\n📝 STEP 6: Testing context_agent_node logic directly")
    
    # Extract the exact logic from context_agent_node
    student_state = initial_state["student_state"]
    last_message = initial_state["last_message"]
    
    user_messages = [msg['content'] for msg in student_state.messages if msg.get('role') == 'user']
    
    is_first_message = len(user_messages) == 0 or (
        len(user_messages) == 2 and 
        student_state.current_design_brief and
        last_message != student_state.current_design_brief and
        len([msg for msg in student_state.messages if msg.get('role') == 'assistant']) == 0
    )
    
    print(f"Context agent node logic:")
    print(f"  - Total messages in state: {len(student_state.messages)}")
    print(f"  - User messages found: {len(user_messages)}")
    print(f"  - Is first message: {is_first_message}")
    print(f"  - Message roles: {[msg.get('role', 'unknown') for msg in student_state.messages]}")
    
    # Step 7: Test the route_decision logic
    print("\n📝 STEP 7: Testing route_decision logic")
    
    # Simulate what would happen in route_decision
    classification = {"is_first_message": is_first_message}
    
    # PRIORITY 2: First message detection
    if classification.get("is_first_message", False):
        print("🎯 First message detected - would route to progressive_opening")
        routing_path = "progressive_opening"
    else:
        print("🔄 Not first message - would use normal routing")
        routing_path = "knowledge_only"  # This is what's happening
    
    print(f"Routing path: {routing_path}")
    
    return is_first_message, routing_path

if __name__ == "__main__":
    result = asyncio.run(debug_message_flow())
    print(f"\n🎯 FINAL RESULT: {result}") 