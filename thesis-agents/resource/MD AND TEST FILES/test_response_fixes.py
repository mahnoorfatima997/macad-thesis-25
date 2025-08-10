#!/usr/bin/env python3
"""
Test script to verify response length and context understanding fixes
"""

import sys
import os
import asyncio
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append('thesis-agents')

from thesis_agents.agents.socratic_tutor import SocraticTutorAgent
from thesis_agents.state_manager import ArchMentorState, StudentProfile

def test_detailed_project_brief_response():
    """Test that detailed project briefs get concise, relevant responses"""
    
    print("🧪 Testing Detailed Project Brief Response")
    print("=" * 50)
    
    # Initialize the Socratic Tutor
    socratic_tutor = SocraticTutorAgent(domain="architecture")
    
    # Create a test state with a detailed project brief
    student_profile = StudentProfile(
        skill_level="intermediate",
        learning_style="visual",
        cognitive_load=0.3,
        engagement_level=0.7,
        knowledge_gaps=["site analysis", "sustainability principles"],
        strengths=["design thinking", "spatial awareness"]
    )
    
    detailed_brief = """
    Hi there, thank you — I'm excited to start this journey too.
    To begin, the primary purpose of my design is to create a vibrant and inclusive community hub that serves as a shared space for learning, recreation, celebration, and support. I want it to be a place where people from all walks of life feel welcome and represented.

    The main users are the residents of a diverse urban neighborhood — that includes families, young people, seniors, immigrants, artists, and local organizations. Their needs vary widely: flexible spaces for workshops and meetings, quiet zones for study or counseling, recreational areas, and venues for cultural events.

    The most important function the space needs to serve is connection — social connection, cultural exchange, and access to resources. The architecture should support that through clear circulation, inclusive programming, and warm, adaptable spaces that reflect the community's identity.

    Now, thinking about the site:

    It's a former industrial warehouse (150m x 80m, 12m high), so structurally, I'm working with large open spans and a significant vertical volume, which is great for flexible planning.

    Located in a dense urban neighborhood, the site is likely surrounded by mixed-use buildings. That means street-level activation and visual permeability are key — the center shouldn't feel closed-off.

    Given its size and former use, I'll need to assess environmental remediation, and possibly consider daylighting strategies since warehouses often have limited window openings.

    The flatness of the site is an advantage for accessibility and circulation, and the existing industrial shell offers potential for adaptive reuse — both for sustainability and community memory.

    I'll also look into zoning constraints — particularly for public occupancy, egress, and parking requirements — though I imagine much of the traffic will be pedestrian and public transit-based.

    Southern exposure may help optimize natural lighting if I can open up the façade or roof — possibly introducing clerestories or light wells.

    My next step is to do a more detailed opportunity and constraint mapping, and start defining how the existing warehouse structure might influence my layout strategies.
    """
    
    state = ArchMentorState(
        student_profile=student_profile,
        messages=[
            {
                "role": "user",
                "content": detailed_brief
            }
        ],
        current_design_brief="Design a sustainable community center for an urban neighborhood"
    )
    
    # Test the response strategy determination
    print("\n1. Testing response strategy determination...")
    
    # Create mock analysis result
    analysis_result = {
        "building_type": "community center",
        "skill_level": "intermediate",
        "current_phase": "discovery"
    }
    
    # Test student analysis
    student_analysis = socratic_tutor._analyze_student_state(state, analysis_result, None)
    conversation_progression = socratic_tutor._analyze_conversation_progression(state, detailed_brief)
    
    # Determine response strategy
    response_strategy = socratic_tutor._determine_response_strategy(student_analysis, conversation_progression)
    
    print(f"✅ Response Strategy: {response_strategy}")
    print(f"✅ Message Length: {len(detailed_brief.split())} words")
    print(f"✅ Is Detailed Brief: {len(detailed_brief.split()) > 100}")
    
    # Test response generation
    print("\n2. Testing response generation...")
    
    try:
        # Test supportive guidance for detailed brief
        response_text = socratic_tutor._get_supportive_architectural_guidance(
            "project_brief", 
            "community center", 
            {"last_message": detailed_brief}
        )
        
        print(f"✅ Generated Response Length: {len(response_text)} characters")
        print(f"✅ Response Word Count: {len(response_text.split())} words")
        print(f"✅ Response Preview: {response_text[:100]}...")
        
        # Check if response is concise
        if len(response_text.split()) <= 50:
            print("✅ Response is concise (≤50 words)")
        else:
            print("❌ Response is too long (>50 words)")
        
        # Check if response is relevant
        if "community" in response_text.lower() or "warehouse" in response_text.lower():
            print("✅ Response is relevant to the project context")
        else:
            print("❌ Response may not be relevant to the project context")
            
    except Exception as e:
        print(f"❌ Response generation failed: {e}")
    
    print("\n✅ Detailed project brief test completed!")

async def test_short_message_response():
    """Test that short messages get appropriate responses"""
    
    print("\n🧪 Testing Short Message Response")
    print("=" * 50)
    
    # Initialize the Socratic Tutor
    socratic_tutor = SocraticTutorAgent(domain="architecture")
    
    # Create a test state with a short message
    student_profile = StudentProfile(
        skill_level="intermediate",
        learning_style="visual",
        cognitive_load=0.3,
        engagement_level=0.7,
        knowledge_gaps=["site analysis", "sustainability principles"],
        strengths=["design thinking", "spatial awareness"]
    )
    
    short_message = "I need help with site analysis for my community center project."
    
    state = ArchMentorState(
        student_profile=student_profile,
        messages=[
            {
                "role": "user",
                "content": short_message
            }
        ],
        current_design_brief="Design a sustainable community center for an urban neighborhood"
    )
    
    # Test the response strategy determination
    print("\n1. Testing response strategy determination...")
    
    # Create mock analysis result
    analysis_result = {
        "building_type": "community center",
        "skill_level": "intermediate",
        "current_phase": "discovery"
    }
    
    # Test student analysis
    student_analysis = socratic_tutor._analyze_student_state(state, analysis_result, None)
    conversation_progression = socratic_tutor._analyze_conversation_progression(state, short_message)
    
    # Determine response strategy
    response_strategy = socratic_tutor._determine_response_strategy(student_analysis, conversation_progression)
    
    print(f"✅ Response Strategy: {response_strategy}")
    print(f"✅ Message Length: {len(short_message.split())} words")
    print(f"✅ Is Detailed Brief: {len(short_message.split()) > 100}")
    
    # Test response generation
    print("\n2. Testing response generation...")
    
    try:
        # Test topic-specific guidance for short message
        response_text = await socratic_tutor._generate_topic_specific_guidance(
            "site analysis", 
            "community center", 
            short_message, 
            {"last_message": short_message}
        )
        
        print(f"✅ Generated Response Length: {len(response_text)} characters")
        print(f"✅ Response Word Count: {len(response_text.split())} words")
        print(f"✅ Response Preview: {response_text[:100]}...")
        
        # Check if response is concise
        if len(response_text.split()) <= 50:
            print("✅ Response is concise (≤50 words)")
        else:
            print("❌ Response is too long (>50 words)")
        
        # Check if response is relevant
        if "site" in response_text.lower() or "analysis" in response_text.lower():
            print("✅ Response is relevant to the topic")
        else:
            print("❌ Response may not be relevant to the topic")
            
    except Exception as e:
        print(f"❌ Response generation failed: {e}")
    
    print("\n✅ Short message test completed!")

async def main():
    """Run all tests"""
    test_detailed_project_brief_response()
    await test_short_message_response()

if __name__ == "__main__":
    asyncio.run(main())
