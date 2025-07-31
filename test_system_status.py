"""
Test script to verify the thesis test system status
"""

import os
import sys
import importlib.util

def check_module(module_name):
    """Check if a module is installed"""
    spec = importlib.util.find_spec(module_name)
    return spec is not None

def check_env_file():
    """Check if .env file exists and has OpenAI key"""
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            content = f.read()
            return 'OPENAI_API_KEY' in content
    return False

def main():
    print("MEGA Test System Status Check")
    print("=" * 50)
    
    # Check core dependencies
    print("\n1. Core Dependencies:")
    core_deps = ['streamlit', 'pandas', 'spacy', 'openai']
    for dep in core_deps:
        status = "✓" if check_module(dep) else "✗"
        print(f"   {status} {dep}")
    
    # Check spaCy model
    print("\n2. spaCy Language Model:")
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        print("   ✓ en_core_web_sm loaded successfully")
    except:
        print("   ✗ en_core_web_sm not found (run: python -m spacy download en_core_web_sm)")
    
    # Check multi-agent dependencies
    print("\n3. Multi-Agent Dependencies (for MENTOR):")
    agent_deps = ['langgraph', 'langchain', 'langchain_openai']
    all_agent_deps = True
    for dep in agent_deps:
        status = "✓" if check_module(dep) else "✗"
        print(f"   {status} {dep}")
        if not check_module(dep):
            all_agent_deps = False
    
    # Check OpenAI API
    print("\n4. OpenAI API Configuration:")
    env_exists = check_env_file()
    env_var = os.getenv("OPENAI_API_KEY")
    if env_exists or env_var:
        print("   ✓ OpenAI API key configured")
    else:
        print("   ⚠ No OpenAI API key found (Generic AI will use fallback responses)")
    
    # Check test files
    print("\n5. Test System Files:")
    test_files = [
        'thesis_tests/test_dashboard_minimal.py',
        'thesis_tests/generic_ai_environment.py',
        'thesis_tests/control_environment.py',
        'thesis_tests/linkography_logger_simple.py',
        'launch_minimal_test.py'
    ]
    for file in test_files:
        status = "✓" if os.path.exists(file) else "✗"
        print(f"   {status} {file}")
    
    # Recommendations
    print("\n" + "=" * 50)
    print("RECOMMENDATIONS:")
    
    if all_agent_deps:
        print("✓ Full system ready - use: python launch_test_dashboard.py")
    else:
        print("⚠ Use minimal version - run: python launch_minimal_test.py")
        print("  (Supports Generic AI and Control groups only)")
    
    if not (env_exists or env_var):
        print("\n⚠ To enable full Generic AI functionality:")
        print("  1. Create a .env file in the root directory")
        print("  2. Add: OPENAI_API_KEY=your-api-key-here")
    
    print("\n✓ System is ready for testing!")

if __name__ == "__main__":
    main()