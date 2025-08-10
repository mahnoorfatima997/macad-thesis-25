#!/usr/bin/env python3
"""
Test script for ContextAgent update to AgentResponse format
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env')

# Add thesis-agents to path
thesis_agents_path = os.path.join(os.getcwd(), 'thesis-agents')
sys.path.append(thesis_agents_path)

from agents.context_agent import ContextAgent
from state_manager import ArchMentorState, StudentProfile
from utils.agent_response import AgentResponse

async def test_context_agent_update():
    """Test ContextAgent update to AgentResponse format"""
    
    print("🧪 Testing ContextAgent update to AgentResponse format...")
    
    try:
        # Create test state
        state = ArchMentorState()
        state.student_profile = StudentProfile(
            skill_level="intermediate",
            learning_style="visual"
        )
        state.current_design_brief = "Design a community center for 200 people with accessible entrances"
        
        # Add conversation history
        state.messages = [
            {"role": "user", "content": "I'm working on the accessibility features"},
            {"role": "assistant", "content": "That's important to consider. What specific accessibility requirements are you thinking about?"},
            {"role": "user", "content": "I think my design is obviously perfect for accessibility"}
        ]
        
        # Create ContextAgent
        agent = ContextAgent("architecture")
        
        # Test input
        current_input = "Obviously my door widths are optimal and clearly meet all requirements"
        
        print(f"📝 Testing with input: {current_input}")
        
        # Get context analysis
        result = await agent.analyze_student_input(state, current_input)
        
        # Check if result is AgentResponse
        print(f"\n📊 Response Analysis:")
        print(f"   Response type: {type(result)}")
        print(f"   Is AgentResponse: {isinstance(result, AgentResponse)}")
        
        if isinstance(result, AgentResponse):
            print(f"   ✅ SUCCESS: ContextAgent returns AgentResponse")
            
            # Check response fields
            print(f"   Response text: {result.response_text[:100]}...")
            print(f"   Response type: {result.response_type}")
            print(f"   Agent name: {result.agent_name}")
            print(f"   Has enhancement metrics: {result.enhancement_metrics is not None}")
            print(f"   Cognitive flags count: {len(result.cognitive_flags)}")
            
            # Check metadata for backward compatibility
            if result.metadata:
                print(f"\n📋 Metadata Analysis (for interaction_logger compatibility):")
                
                # Check for required fields that interaction_logger expects
                required_fields = [
                    "core_classification", "content_analysis", "conversation_patterns",
                    "routing_suggestions", "agent_contexts", "design_phase",
                    "context_quality", "timestamp", "agent", "conversation_history"
                ]
                
                missing_fields = []
                for field in required_fields:
                    if field not in result.metadata:
                        missing_fields.append(field)
                    else:
                        print(f"   ✅ {field}: Present")
                
                if missing_fields:
                    print(f"   ❌ Missing fields for interaction_logger: {missing_fields}")
                else:
                    print(f"   ✅ All required fields present for interaction_logger compatibility")
                
                # Check core_classification structure
                core_classification = result.metadata.get("core_classification", {})
                classification_fields = [
                    "interaction_type", "understanding_level", "confidence_level", 
                    "engagement_level", "overconfidence_score", "is_technical_question",
                    "is_feedback_request", "is_example_request", "shows_confusion",
                    "requests_help", "demonstrates_overconfidence", "seeks_validation"
                ]
                
                missing_classification_fields = []
                for field in classification_fields:
                    if field not in core_classification:
                        missing_classification_fields.append(field)
                
                if missing_classification_fields:
                    print(f"   ❌ Missing classification fields: {missing_classification_fields}")
                else:
                    print(f"   ✅ All classification fields present")
                
                # Check content_analysis structure
                content_analysis = result.metadata.get("content_analysis", {})
                content_fields = [
                    "word_count", "sentence_count", "question_count", "technical_terms",
                    "emotional_indicators", "complexity_score", "specificity_score"
                ]
                
                missing_content_fields = []
                for field in content_fields:
                    if field not in content_analysis:
                        missing_content_fields.append(field)
                
                if missing_content_fields:
                    print(f"   ❌ Missing content analysis fields: {missing_content_fields}")
                else:
                    print(f"   ✅ All content analysis fields present")
                
                # Check conversation_patterns structure
                conversation_patterns = result.metadata.get("conversation_patterns", {})
                pattern_fields = [
                    "repetitive_topics", "topic_jumping", "engagement_trend",
                    "understanding_progression", "conversation_depth", "recent_focus"
                ]
                
                missing_pattern_fields = []
                for field in pattern_fields:
                    if field not in conversation_patterns:
                        missing_pattern_fields.append(field)
                
                if missing_pattern_fields:
                    print(f"   ❌ Missing conversation pattern fields: {missing_pattern_fields}")
                else:
                    print(f"   ✅ All conversation pattern fields present")
                
                # Check routing_suggestions structure
                routing_suggestions = result.metadata.get("routing_suggestions", {})
                routing_fields = [
                    "primary_route", "suggested_agents", "response_type",
                    "priority", "confidence", "reasoning"
                ]
                
                missing_routing_fields = []
                for field in routing_fields:
                    if field not in routing_suggestions:
                        missing_routing_fields.append(field)
                
                if missing_routing_fields:
                    print(f"   ❌ Missing routing suggestion fields: {missing_routing_fields}")
                else:
                    print(f"   ✅ All routing suggestion fields present")
                
                # Check agent_contexts structure
                agent_contexts = result.metadata.get("agent_contexts", {})
                expected_agents = ["knowledge_agent", "socratic_agent", "cognitive_agent", "analysis_agent"]
                
                missing_agents = []
                for agent in expected_agents:
                    if agent not in agent_contexts:
                        missing_agents.append(agent)
                
                if missing_agents:
                    print(f"   ❌ Missing agent contexts: {missing_agents}")
                else:
                    print(f"   ✅ All agent contexts present")
                
                # Check design_phase structure
                design_phase = result.metadata.get("design_phase", {})
                phase_fields = [
                    "current_phase", "previous_phase", "phase_transition",
                    "phase_scores", "confidence", "phase_indicators"
                ]
                
                missing_phase_fields = []
                for field in phase_fields:
                    if field not in design_phase:
                        missing_phase_fields.append(field)
                
                if missing_phase_fields:
                    print(f"   ❌ Missing design phase fields: {missing_phase_fields}")
                else:
                    print(f"   ✅ All design phase fields present")
                
                # Check cognitive offloading patterns
                cognitive_offloading = result.metadata.get("cognitive_offloading_patterns", {})
                offloading_fields = [
                    "detected", "type", "confidence", "indicators", "mitigation_strategy"
                ]
                
                missing_offloading_fields = []
                for field in offloading_fields:
                    if field not in cognitive_offloading:
                        missing_offloading_fields.append(field)
                
                if missing_offloading_fields:
                    print(f"   ❌ Missing cognitive offloading fields: {missing_offloading_fields}")
                else:
                    print(f"   ✅ All cognitive offloading fields present")
                
                print(f"\n🎯 Summary:")
                print(f"   Interaction Type: {core_classification.get('interaction_type', 'unknown')}")
                print(f"   Understanding Level: {core_classification.get('understanding_level', 'unknown')}")
                print(f"   Confidence Level: {core_classification.get('confidence_level', 'unknown')}")
                print(f"   Engagement Level: {core_classification.get('engagement_level', 'unknown')}")
                print(f"   Overconfidence Score: {core_classification.get('overconfidence_score', 0)}")
                print(f"   Context Quality: {result.metadata.get('context_quality', 0):.2f}")
                print(f"   Primary Route: {routing_suggestions.get('primary_route', 'unknown')}")
                print(f"   Cognitive Offloading Detected: {cognitive_offloading.get('detected', False)}")
                
            else:
                print(f"   ❌ ERROR: No metadata found in AgentResponse")
                
        else:
            print(f"   ❌ ERROR: ContextAgent does not return AgentResponse")
            print(f"   Actual return type: {type(result)}")
            if isinstance(result, dict):
                print(f"   Dict keys: {list(result.keys())}")
    
    except Exception as e:
        print(f"❌ ERROR during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_context_agent_update()) 