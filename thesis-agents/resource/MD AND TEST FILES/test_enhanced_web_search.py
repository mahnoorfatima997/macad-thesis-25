#!/usr/bin/env python3
"""
Test script for enhanced web search functionality in DomainExpertAgent
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Add the thesis-agents directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'thesis-agents'))

from agents.domain_expert import DomainExpertAgent, analyze_conversation_context_for_search, generate_context_aware_search_query
from state_manager import ArchMentorState, StudentProfile, VisualArtifact, DesignPhase

async def test_enhanced_web_search():
    """Test the enhanced web search with context awareness"""
    
    print("🧪 Testing Enhanced Web Search Functionality")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Create a test state with conversation context
    student_profile = StudentProfile(
        skill_level="beginner",
        learning_style="visual",
        cognitive_load=0.3,
        engagement_level=0.8
    )
    
    # Create visual artifacts (empty for this test)
    visual_artifacts = []
    
    # Create state with conversation history
    state = ArchMentorState(
        student_profile=student_profile,
        visual_artifacts=visual_artifacts,
        design_phase=DesignPhase.IDEATION,
        messages=[
            {"role": "user", "content": "I want to design a community center for adaptive reuse"},
            {"role": "assistant", "content": "Great! Adaptive reuse is an excellent approach. What type of building are you considering converting?"},
            {"role": "user", "content": "I'm thinking of converting an old warehouse with steel beams"},
            {"role": "assistant", "content": "Steel beams offer great structural possibilities. What specific functions will your community center serve?"},
            {"role": "user", "content": "I need examples of successful adaptive reuse projects"}
        ]
    )
    
    # Test 1: Context Analysis
    print("\n🔍 Test 1: Context Analysis")
    print("-" * 30)
    
    context = analyze_conversation_context_for_search(state)
    print(f"Extracted context: {context}")
    
    expected_context_elements = [
        "building_type" in context,
        "specific_elements" in context,
        "user_needs" in context,
        "adaptive_reuse" in context.get("user_needs", [])
    ]
    
    print(f"✅ Context analysis working: {all(expected_context_elements)}")
    
    # Test 2: Context-Aware Query Generation
    print("\n🔍 Test 2: Context-Aware Query Generation")
    print("-" * 30)
    
    topic = "adaptive reuse examples"
    search_query = generate_context_aware_search_query(topic, context)
    print(f"Generated query: {search_query}")
    
    # Check if query includes context elements
    query_quality_checks = [
        "adaptive reuse" in search_query.lower(),
        "community" in search_query.lower(),
        "warehouse" in search_query.lower(),
        "steel" in search_query.lower(),
        "site:" in search_query  # Should include architectural sources
    ]
    
    print(f"✅ Query quality: {sum(query_quality_checks)}/{len(query_quality_checks)} checks passed")
    
    # Test 3: Enhanced Web Search
    print("\n🔍 Test 3: Enhanced Web Search")
    print("-" * 30)
    
    try:
        domain_expert = DomainExpertAgent()
        
        # Test search with context
        print("Searching for 'adaptive reuse examples' with context...")
        results = await domain_expert.search_web_for_knowledge("adaptive reuse examples", state)
        
        if results:
            print(f"✅ Found {len(results)} results")
            print(f"✅ Results have context metadata: {'context_used' in results[0].get('metadata', {})}")
            print(f"✅ Results have relevance scores: {'relevance_score' in results[0].get('metadata', {})}")
            
            # Show first result details
            first_result = results[0]
            print(f"\n📋 First result:")
            print(f"   Title: {first_result['metadata'].get('title', 'N/A')}")
            print(f"   Source: {first_result['metadata'].get('source', 'N/A')}")
            print(f"   Relevance Score: {first_result['metadata'].get('relevance_score', 'N/A')}")
            print(f"   Content Preview: {first_result['content'][:100]}...")
        else:
            print("⚠️ No results found (this might be normal if search fails)")
            
    except Exception as e:
        print(f"⚠️ Web search test failed: {e}")
        print("This is expected if there are network issues or API problems")
    
    # Test 4: Different Context Scenarios
    print("\n🔍 Test 4: Different Context Scenarios")
    print("-" * 30)
    
    # Test with accessibility focus
    accessibility_state = ArchMentorState(
        student_profile=student_profile,
        visual_artifacts=visual_artifacts,
        design_phase=DesignPhase.IDEATION,
        messages=[
            {"role": "user", "content": "I need to make my community center accessible for elderly users"},
            {"role": "assistant", "content": "Accessibility is crucial. What specific accessibility features are you considering?"},
            {"role": "user", "content": "I need examples of accessible community centers"}
        ]
    )
    
    accessibility_context = analyze_conversation_context_for_search(accessibility_state)
    accessibility_query = generate_context_aware_search_query("accessible community centers", accessibility_context)
    
    print(f"Accessibility context: {accessibility_context}")
    print(f"Accessibility query: {accessibility_query}")
    
    # Check if accessibility is included
    accessibility_included = "accessibility" in accessibility_query.lower() or "accessible" in accessibility_query.lower()
    print(f"✅ Accessibility included in query: {accessibility_included}")
    
    print("\n🎉 Enhanced Web Search Test Complete!")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(test_enhanced_web_search()) 