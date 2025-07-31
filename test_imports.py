"""
Test script to verify all imports work correctly
"""

import sys
import os

# Add directories to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
thesis_agents_dir = os.path.join(current_dir, 'thesis-agents')
sys.path.insert(0, thesis_agents_dir)

print("Testing imports...")
print(f"Current directory: {current_dir}")
print(f"Python path: {sys.path[:3]}")
print("-" * 50)

# Test basic imports
try:
    print("Testing thesis_tests imports...")
    from thesis_tests.data_models import TestSession, DesignMove
    print("✅ Data models imported successfully")
    
    from thesis_tests.logging_system import TestSessionLogger
    print("✅ Logging system imported successfully")
    
    from thesis_tests.linkography_logger import LinkographyLogger
    print("✅ Linkography logger imported successfully")
    
    from thesis_tests.assessment_tools import PreTestAssessment
    print("✅ Assessment tools imported successfully")
    
    from thesis_tests.move_parser import MoveParser
    print("✅ Move parser imported successfully")
    
except Exception as e:
    print(f"❌ Error importing thesis_tests modules: {e}")

print("-" * 50)

# Test multi-agent imports
try:
    print("Testing multi-agent system imports...")
    from orchestration.langgraph_orchestrator import LangGraphOrchestrator
    print("✅ LangGraph orchestrator imported successfully")
    
    from state_manager import ArchMentorState, StudentProfile
    print("✅ State manager imported successfully")
    
except Exception as e:
    print(f"❌ Error importing multi-agent modules: {e}")
    print("   This is expected if the multi-agent system is not fully configured")

print("-" * 50)

# Test benchmarking imports
try:
    print("Testing benchmarking imports...")
    from benchmarking.linkography_engine import LinkographyEngine
    print("✅ Linkography engine imported successfully")
    
    from benchmarking.linkography_types import DesignMove as LinkographyMove
    print("✅ Linkography types imported successfully")
    
except Exception as e:
    print(f"❌ Error importing benchmarking modules: {e}")

print("-" * 50)

# Test environment imports
try:
    print("Testing environment imports...")
    from thesis_tests.control_environment import ControlTestEnvironment
    print("✅ Control environment imported successfully")
    
    from thesis_tests.generic_ai_environment import GenericAITestEnvironment
    print("✅ Generic AI environment imported successfully")
    
    # MENTOR environment might fail due to multi-agent dependencies
    from thesis_tests.mentor_environment import MentorTestEnvironment
    print("✅ MENTOR environment imported successfully")
    
except Exception as e:
    print(f"❌ Error importing environment modules: {e}")

print("-" * 50)
print("Import test complete!")
print("\nTo run the test dashboard, use:")
print("  python run_test_dashboard.py")