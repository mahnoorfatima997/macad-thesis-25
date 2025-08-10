#!/usr/bin/env python3
"""
Test script for state validation integration in orchestrator
"""

import sys
import os
from dotenv import load_dotenv

# Add the thesis-agents directory to the path
thesis_agents_path = os.path.join(os.path.dirname(__file__), 'thesis-agents')
sys.path.append(thesis_agents_path)

# Load environment variables
load_dotenv('.env')

from orchestration.langgraph_orchestrator import LangGraphOrchestrator
from state_manager import ArchMentorState, StudentProfile, DesignPhase
from utils.state_validator import StateValidator, StateMonitor

def test_state_validation_integration():
    """Test the state validation integration in orchestrator"""
    
    print("🧪 Testing State Validation Integration in Orchestrator")
    print("=" * 70)
    
    try:
        # Initialize the orchestrator
        print("1. Initializing orchestrator...")
        orchestrator = LangGraphOrchestrator(domain="architecture")
        print("✅ Orchestrator initialized successfully")
        
        # Test that the state validation system is properly initialized
        print("\n2. Testing state validation system initialization...")
        if hasattr(orchestrator, 'state_validator'):
            print("✅ StateValidator is initialized")
        else:
            print("❌ StateValidator not found")
            return False
            
        if hasattr(orchestrator, 'state_monitor'):
            print("✅ StateMonitor is initialized")
        else:
            print("❌ StateMonitor not found")
            return False
        
        # Test state validation functionality
        print("\n3. Testing state validation functionality...")
        state_validator = orchestrator.state_validator
        state_monitor = orchestrator.state_monitor
        
        # Create a test workflow state
        test_student_state = ArchMentorState(
            student_profile=StudentProfile(
                skill_level="beginner",
                learning_style="visual",
                cognitive_load=0.3,
                engagement_level=0.7
            ),
            messages=[],
            current_design_brief="Community Center Project",
            design_phase=DesignPhase.IDEATION,
            visual_artifacts=[],
            domain="architecture"
        )
        
        test_state = {
            "student_state": test_student_state,
            "last_message": "Can you show me some examples of sustainable architecture?",
            "student_classification": {
                "interaction_type": "example_request",
                "confidence_level": "confident",
                "understanding_level": "medium",
                "engagement_level": "high"
            },
            "context_analysis": {
                "conversation_patterns": {
                    "recent_messages": ["Hello", "I'm working on a project"],
                    "repetitive_topics": False
                }
            },
            "routing_suggestions": {
                "primary_route": "knowledge_only",
                "confidence": 0.8,
                "reasoning": ["User requested examples", "Clear knowledge request"]
            },
            "routing_decision": {}
        }
        
        # Test state validation
        validation_result = state_validator.validate_state(test_state)
        print(f"✅ State validation result: {validation_result.is_valid}")
        if not validation_result.is_valid:
            print(f"   Errors: {validation_result.errors}")
        
        # Test state monitoring
        print("\n4. Testing state monitoring...")
        state_monitor.record_state_change(test_state, "test_node_input")
        state_monitor.record_state_change(test_state, "test_node_output")
        
        # Get monitoring statistics
        stats = state_monitor.get_state_summary()
        print(f"✅ State monitoring statistics: {stats}")
        
        # Test state validation in orchestrator nodes
        print("\n5. Testing state validation in orchestrator nodes...")
        
        # Test context agent node validation
        context_validation = orchestrator.state_validator.validate_state(test_state)
        print(f"✅ Context agent node validation: {context_validation.is_valid}")
        
        # Test router node validation
        router_validation = orchestrator.state_validator.validate_state(test_state)
        print(f"✅ Router node validation: {router_validation.is_valid}")
        
        # Test analysis agent node validation
        analysis_validation = orchestrator.state_validator.validate_state(test_state)
        print(f"✅ Analysis agent node validation: {analysis_validation.is_valid}")
        
        # Test domain expert node validation
        domain_validation = orchestrator.state_validator.validate_state(test_state)
        print(f"✅ Domain expert node validation: {domain_validation.is_valid}")
        
        # Test socratic tutor node validation
        socratic_validation = orchestrator.state_validator.validate_state(test_state)
        print(f"✅ Socratic tutor node validation: {socratic_validation.is_valid}")
        
        # Test cognitive enhancement node validation
        cognitive_validation = orchestrator.state_validator.validate_state(test_state)
        print(f"✅ Cognitive enhancement node validation: {cognitive_validation.is_valid}")
        
        # Test synthesizer node validation
        synthesizer_validation = orchestrator.state_validator.validate_state(test_state)
        print(f"✅ Synthesizer node validation: {synthesizer_validation.is_valid}")
        
        # Test anomaly detection
        print("\n6. Testing anomaly detection...")
        
        # Create an invalid state (missing required fields)
        invalid_state = {
            "student_state": test_student_state,
            # Missing required fields like last_message, student_classification, etc.
        }
        
        invalid_validation = state_validator.validate_state(invalid_state)
        print(f"✅ Invalid state detection: {not invalid_validation.is_valid}")
        if not invalid_validation.is_valid:
            print(f"   Detected errors: {invalid_validation.errors}")
        
        # Test state monitoring with invalid state
        state_monitor.record_state_change(invalid_state, "invalid_test_input")
        anomalies = state_monitor.detect_anomalies()
        print(f"✅ Anomaly detection: {len(anomalies)} anomalies found")
        
        print("\n🎉 All state validation integration tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_state_validation_integration()
    if success:
        print("\n✅ State validation integration test completed successfully!")
    else:
        print("\n❌ State validation integration test failed!")
        sys.exit(1) 
