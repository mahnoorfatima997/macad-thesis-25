"""
Verify that the MENTOR multi-agent system is fully operational
"""

import sys
import os

def check_import(module_name, import_statement):
    """Check if a module can be imported"""
    try:
        exec(import_statement)
        return True, "[OK] Installed"
    except ImportError as e:
        return False, f"[MISSING] {str(e)}"
    except Exception as e:
        return False, f"[ERROR] {str(e)}"

def main():
    print("MENTOR Multi-Agent System Verification")
    print("=" * 50)
    
    # Check core dependencies
    print("\n1. Core Dependencies:")
    dependencies = [
        ("LangGraph", "import langgraph"),
        ("LangChain", "import langchain"),
        ("OpenAI", "import openai"),
        ("OpenCV", "import cv2"),
        ("ChromaDB", "import chromadb"),
        ("Streamlit", "import streamlit"),
    ]
    
    all_good = True
    for name, import_stmt in dependencies:
        success, message = check_import(name, import_stmt)
        print(f"   {name}: {message}")
        if not success:
            all_good = False
    
    # Check multi-agent system
    print("\n2. Multi-Agent System Components:")
    
    # Add thesis-agents to path
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    thesis_agents_dir = os.path.join(parent_dir, 'thesis-agents')
    sys.path.insert(0, thesis_agents_dir)
    
    components = [
        ("LangGraph Orchestrator", "from orchestration.langgraph_orchestrator import LangGraphOrchestrator"),
        ("State Manager", "from state_manager import ArchMentorState, StudentProfile"),
        ("Analysis Agent", "from agents.analysis_agent import AnalysisAgent"),
        ("Socratic Tutor", "from agents.socratic_tutor import SocraticTutorAgent"),
        ("Domain Expert", "from agents.domain_expert import DomainExpertAgent"),
        ("Cognitive Enhancement", "from agents.cognitive_enhancement import CognitiveEnhancementAgent"),
        ("Context Agent", "from agents.context_agent import ContextAgent"),
    ]
    
    for name, import_stmt in components:
        success, message = check_import(name, import_stmt)
        print(f"   {name}: {message}")
        if not success:
            all_good = False
    
    # Check test system
    print("\n3. Test System Components:")
    sys.path.insert(0, parent_dir)
    
    test_components = [
        ("MENTOR Environment", "from thesis_tests.mentor_environment import MentorTestEnvironment, MENTOR_AVAILABLE"),
        ("Generic AI Environment", "from thesis_tests.generic_ai_environment import GenericAITestEnvironment"),
        ("Control Environment", "from thesis_tests.control_environment import ControlTestEnvironment"),
        ("Linkography Logger", "from thesis_tests.linkography_logger_simple import SimpleLinkographyLogger"),
    ]
    
    for name, import_stmt in test_components:
        success, message = check_import(name, import_stmt)
        print(f"   {name}: {message}")
        if not success:
            all_good = False
    
    # Final verdict
    print("\n" + "=" * 50)
    if all_good:
        print("[SUCCESS] MENTOR SYSTEM FULLY OPERATIONAL!")
        print("\nYou can now run the full cognitive benchmarking test:")
        print("   python launch_full_test.py")
    else:
        print("[FAIL] Some components are missing.")
        print("\nPlease install missing dependencies:")
        print("   pip install -r thesis-agents/requirements.txt")
        print("   pip install -r thesis_tests/requirements_tests.txt")
    
    # Check MENTOR availability flag
    try:
        from thesis_tests.mentor_environment import MENTOR_AVAILABLE
        print(f"\nMENTOR_AVAILABLE flag: {MENTOR_AVAILABLE}")
    except:
        print("\nCould not check MENTOR_AVAILABLE flag")

if __name__ == "__main__":
    main()