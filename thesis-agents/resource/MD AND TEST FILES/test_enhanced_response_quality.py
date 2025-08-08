#!/usr/bin/env python3
"""
Test script for enhanced response quality in SocraticTutorAgent
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Add the thesis-agents directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'thesis-agents'))

from agents.socratic_tutor import SocraticTutorAgent
from state_manager import ArchMentorState, StudentProfile, VisualArtifact, DesignPhase

async def test_enhanced_response_quality():
    """Test the enhanced response quality with specific architectural guidance"""
    
    print("🧪 Testing Enhanced Response Quality")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Create Socratic tutor agent
    socratic_tutor = SocraticTutorAgent()
    
    # Create test state
    student_profile = StudentProfile(
        skill_level="beginner",
        learning_style="visual",
        cognitive_load=0.3,
        engagement_level=0.8
    )
    
    visual_artifacts = []
    
    # Test cases for different response types
    test_cases = [
        {
            "name": "Clarifying Guidance - Circulation",
            "messages": [
                {"role": "user", "content": "I want to design a community center"},
                {"role": "assistant", "content": "Great! Let's start with your vision."},
                {"role": "user", "content": "I'm having trouble with the circulation flow"}
            ],
            "expected_keywords": ["circulation", "user groups", "destinations", "wayfinding"],
            "response_type": "clarifying_guidance"
        },
        {
            "name": "Supportive Guidance - Design",
            "messages": [
                {"role": "user", "content": "I want to design a community center"},
                {"role": "assistant", "content": "Great! Let's start with your vision."},
                {"role": "user", "content": "I'm not sure about the design approach"}
            ],
            "expected_keywords": ["user groups", "activities", "interact", "vision"],
            "response_type": "supportive_guidance"
        },
        {
            "name": "Challenging Question - Layout",
            "messages": [
                {"role": "user", "content": "I want to design a community center"},
                {"role": "assistant", "content": "Great! Let's start with your vision."},
                {"role": "user", "content": "I think the layout should be open plan"}
            ],
            "expected_keywords": ["acoustic separation", "visual connections", "reconfigure"],
            "response_type": "challenging_question"
        },
        {
            "name": "Adaptive Reuse - Materials",
            "messages": [
                {"role": "user", "content": "I want to convert an old warehouse into a community center"},
                {"role": "assistant", "content": "Excellent! Adaptive reuse is a great approach."},
                {"role": "user", "content": "I need help with material choices"}
            ],
            "expected_keywords": ["existing materials", "history", "character", "dialogue"],
            "response_type": "supportive_guidance"
        }
    ]
    
    print("\n🔍 Test 1: Response Quality Assessment")
    print("-" * 30)
    
    for test_case in test_cases:
        print(f"\n📝 Testing: {test_case['name']}")
        
        # Create state with test messages
        state = ArchMentorState(
            student_profile=student_profile,
            visual_artifacts=visual_artifacts,
            design_phase=DesignPhase.IDEATION,
            messages=test_case['messages']
        )
        
        # Mock analysis result
        analysis_result = {
            "understanding_level": "medium",
            "confidence_level": "confident",
            "engagement_level": "high"
        }
        
        try:
            # Generate response
            response = await socratic_tutor.generate_response(state, analysis_result)
            
            # Extract response text
            response_text = response.response_text if hasattr(response, 'response_text') else response.get('response_text', '')
            
            print(f"   Response: {response_text[:100]}...")
            
            # Check for expected keywords
            response_lower = response_text.lower()
            found_keywords = []
            for keyword in test_case['expected_keywords']:
                if keyword.lower() in response_lower:
                    found_keywords.append(keyword)
            
            print(f"   Expected Keywords: {test_case['expected_keywords']}")
            print(f"   Found Keywords: {found_keywords}")
            print(f"   ✅ Keyword Match: {len(found_keywords)}/{len(test_case['expected_keywords'])}")
            
            # Check response quality indicators
            quality_indicators = [
                "specific" in response_lower or "specific" in response_text,
                "architectural" in response_lower or "design" in response_lower,
                "community" in response_lower or "building" in response_lower,
                len(response_text) > 50,  # Substantial response
                "?" in response_text  # Includes questions
            ]
            
            print(f"   Quality Score: {sum(quality_indicators)}/{len(quality_indicators)}")
            
        except Exception as e:
            print(f"   ⚠️ Test failed: {e}")
    
    # Test 2: Specific Guidance Templates
    print("\n🔍 Test 2: Specific Guidance Templates")
    print("-" * 30)
    
    # Test specific architectural guidance
    focus_areas = ["circulation", "lighting", "accessibility", "sustainability"]
    building_types = ["community", "adaptive_reuse"]
    
    for focus_area in focus_areas:
        for building_type in building_types:
            guidance = socratic_tutor._generate_specific_architectural_guidance(focus_area, building_type, "design")
            print(f"\n   {focus_area.title()} - {building_type}:")
            print(f"   {guidance[:80]}...")
            
            # Check if guidance is specific and helpful
            is_specific = len(guidance) > 50 and focus_area.lower() in guidance.lower()
            print(f"   ✅ Specific Guidance: {is_specific}")
    
    # Test 3: Challenging Questions
    print("\n🔍 Test 3: Challenging Questions")
    print("-" * 30)
    
    topics = ["design", "layout", "structure", "materials"]
    building_types = ["community", "adaptive_reuse"]
    
    for topic in topics:
        for building_type in building_types:
            question = socratic_tutor._get_challenging_architectural_question(topic, building_type, {})
            print(f"\n   {topic.title()} - {building_type}:")
            print(f"   {question[:80]}...")
            
            # Check if question is challenging and specific
            is_challenging = "?" in question and len(question) > 50
            is_specific = topic.lower() in question.lower() or building_type.lower() in question.lower()
            print(f"   ✅ Challenging: {is_challenging}")
            print(f"   ✅ Specific: {is_specific}")
    
    print("\n🎉 Enhanced Response Quality Test Complete!")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(test_enhanced_response_quality()) 