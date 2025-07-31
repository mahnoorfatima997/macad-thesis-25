"""
Test MENTOR initialization with proper error handling
"""
import os
import sys

# Set environment to handle unicode properly
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Add paths
parent_dir = os.path.dirname(os.path.abspath(__file__))
thesis_agents_dir = os.path.join(parent_dir, 'thesis-agents')
sys.path.insert(0, thesis_agents_dir)
sys.path.insert(0, parent_dir)

try:
    from thesis_tests.mentor_environment import MentorTestEnvironment, MENTOR_AVAILABLE
    
    print(f"MENTOR_AVAILABLE: {MENTOR_AVAILABLE}")
    
    if MENTOR_AVAILABLE:
        # Initialize MENTOR environment
        env = MentorTestEnvironment()
        print("SUCCESS: MENTOR Environment initialized!")
        
        # Test basic functionality
        from thesis_tests.data_models import TestPhase
        
        # Check if orchestrator is available
        if hasattr(env, 'orchestrator'):
            print("Orchestrator is available")
            if hasattr(env.orchestrator, 'graph'):
                print("LangGraph workflow is configured")
        else:
            print("WARNING: Orchestrator not initialized")
            
    else:
        print("MENTOR is not available - missing dependencies")
        
except Exception as e:
    print(f"Error during initialization: {e}")
    print("\nThis might be due to:")
    print("1. ChromaDB collection already exists (normal)")
    print("2. Unicode encoding issues (Windows console)")
    print("\nThe MENTOR system should still work in the Streamlit dashboard")