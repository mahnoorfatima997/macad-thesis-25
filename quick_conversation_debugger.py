#!/usr/bin/env python3
"""
Quick Conversation Debugger
Helps identify timing issues in the conversation flow
"""

import sys
import os
sys.path.append('./thesis-agents')

from state_manager import ArchMentorState, StudentProfile
from orchestration.langgraph_orchestrator import LangGraphOrchestrator
import asyncio

async def debug_conversation_flow():
    """Debug the conversation flow to identify timing issues"""
    
    print("🔍 Starting conversation flow debug...")
    
    # Initialize orchestrator
    orchestrator = LangGraphOrchestrator("architecture")
    
    # Create initial state
    state = ArchMentorState()
    state.current_design_brief = "I want to design a community center in Copenhagen"
    state.student_profile = StudentProfile(skill_level="intermediate")
    state.domain = "architecture"
    
    # Test the exact conversation flow from your example
    conversation_steps = [
        "What should I consider first for my community center project?",
        "The main purpose is to create a welcoming space for community gatherings, workshops, and cultural events. The users will be mostly locals—families, kids, elderly, and young adults—so the space needs to be flexible and inclusive. I think the most important function is to encourage social interaction and offer a sense of belonging. I'm especially interested in how spatial layout and natural light can support that.",
        "To balance open and intimate spaces, I'd combine a large central gathering area with smaller side rooms or alcoves. The open space would host flexible events like markets or performances, encouraging interaction across age groups. Around it, quieter rooms could serve as lounges, reading nooks, or activity spaces for different age groups—kids, teens, and elders—offering comfort and inclusion.\n\nFor natural light, I'd use large south-facing windows and skylights to bring in warmth during winter, combined with light shelves and diffusing materials to prevent glare in summer. This way, the center stays bright and uplifting year-round, supporting well-being and togetherness.",
        "I see the challenge now—it's not just about bringing in light, but also managing heat and comfort throughout the year. I'm a bit unsure how to design for both warmth in winter and avoid overheating or glare in summer. Should I focus more on external shading, or are dynamic systems like smart glass or artificial lighting controls more effective in a place like Copenhagen? I'd love your help figuring out which strategies make the most sense together.",
        "I am not sure if I understood how external shading devices can be integrated into facade. can you provide examples?",
        "I think seeing examples from other community centers would help most—especially ones that solved similar daylight and shading challenges. I'm still trying to understand how external shading fits into the facade design, both aesthetically and functionally. Can you show examples or diagrams of how it's integrated, maybe in modern Nordic buildings?",
        "I'd love to see successful case studies and problem-solving examples, especially from community projects in Nordic climates. I'm mainly trying to solve how to integrate external shading into the facade in a way that looks good and works well with seasonal light changes.",
        "can you share some example projects for community center in Nordic countries?"
    ]
    
    # Add brief as first message
    state.messages = [
        {"role": "brief", "content": state.current_design_brief}
    ]
    
    print(f"📝 Starting with brief message")
    
    for i, user_input in enumerate(conversation_steps, 1):
        print(f"\n{'='*60}")
        print(f"🎯 Step {i}: {user_input[:50]}...")
        print(f"{'='*60}")
        
        # Add user message to state
        state.messages.append({
            "role": "user",
            "content": user_input
        })
        
        print(f"📝 State messages before processing: {len(state.messages)}")
        user_messages = [msg for msg in state.messages if msg.get('role') == 'user']
        print(f"📊 User messages in state: {len(user_messages)}")
        for j, msg in enumerate(user_messages):
            print(f"  {j}: {msg['content'][:50]}...")
        
        # Process through orchestrator
        print(f"\n🚀 Processing through orchestrator...")
        result = await orchestrator.process_student_input(state)
        
        print(f"✅ Response: {result['response'][:100]}...")
        print(f"✅ Routing path: {result.get('routing_path', 'unknown')}")
        print(f"✅ Response type: {result.get('metadata', {}).get('response_type', 'unknown')}")
        
        # Add assistant response to state
        state.messages.append({
            "role": "assistant",
            "content": result["response"]
        })
        
        print(f"📝 State messages after processing: {len(state.messages)}")
    
    return "Debug complete"

if __name__ == "__main__":
    result = asyncio.run(debug_conversation_flow())
    print(f"\n🔍 {result}") 