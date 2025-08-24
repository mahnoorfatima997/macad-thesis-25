#!/usr/bin/env python3
"""
Test Issue 2: Database search not triggering web search for project examples
"""

import sys
import os
sys.path.append('.')
sys.path.append('thesis-agents')

from dotenv import load_dotenv
load_dotenv()

async def test_database_search_issue():
    """Test if database search properly triggers web search when results lack project names"""
    
    try:
        from agents.domain_expert.adapter import DomainExpertAgent
        from state_manager import ArchMentorState
        
        # Create test state
        state = ArchMentorState()
        state.current_design_brief = "community_center"
        state.messages = [
            {"role": "user", "content": "I'm designing a community center"},
            {"role": "assistant", "content": "Great! Tell me more."},
            {"role": "user", "content": "can you give example projects for community center that has courtyards?"}
        ]
        
        # Create domain expert
        domain_expert = DomainExpertAgent()
        
        print("🧪 TESTING ISSUE 2: Database search → Web search trigger")
        print("=" * 60)
        print("User request: 'can you give example projects for community center that has courtyards?'")
        print("Expected: Should trigger web search if database lacks specific project names")
        print("=" * 60)
        
        # Test the knowledge provision with correct parameters
        context_classification = {
            "user_intent": "knowledge_seeking",
            "user_input": "can you give example projects for community center that has courtyards?",
            "is_project_example_request": True
        }

        analysis_result = {
            "gap_type": "example_gap",
            "project_context": "community_center"
        }

        routing_decision = {
            "route": "knowledge_only",
            "reason": "User requesting project examples"
        }

        result = await domain_expert.provide_knowledge(
            state=state,
            context_classification=context_classification,
            analysis_result=analysis_result,
            routing_decision=routing_decision
        )
        
        print("\n📊 RESULTS:")
        print(f"Response length: {len(result.response_text)}")
        print(f"Response preview: {result.response_text[:200]}...")
        print(f"Sources: {len(result.sources_used)}")
        print(f"Response type: {result.response_type.value}")

        # Check if web search was triggered
        has_web_sources = any('http' in str(source) for source in result.sources_used)

        print(f"\n🔍 ANALYSIS:")
        print(f"Has web sources: {has_web_sources}")
        contains_sorry = "I'm sorry" in result.response_text
        print(f"Contains 'I'm sorry': {contains_sorry}")

        # Also check for cognitive protection message
        is_cognitive_protection = "cognitive protection" in result.response_text.lower()
        print(f"Is cognitive protection: {is_cognitive_protection}")

        if has_web_sources and not contains_sorry:
            print("✅ ISSUE 2 FIXED: Web search was triggered and provided results")
        elif has_web_sources:
            print("⚠️ PARTIAL FIX: Web search triggered but still generic response")
        elif is_cognitive_protection:
            print("⚠️ COGNITIVE PROTECTION: Request blocked as premature - need to adjust test")
        else:
            print("❌ ISSUE 2 NOT FIXED: Web search was not triggered")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_database_search_issue())
