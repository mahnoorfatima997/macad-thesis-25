#!/usr/bin/env python3
"""
Very simple test script for DomainExpertAgent structure without any initialization
"""

import sys
import os

# Add the thesis-agents directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'thesis-agents'))

from utils.agent_response import AgentResponse, ResponseType

def test_domain_expert_structure():
    """Test the DomainExpertAgent structure without initialization"""
    
    print("🧪 Testing DomainExpertAgent Structure...")
    
    # Test that we can import the agent class
    try:
        from agents.domain_expert import DomainExpertAgent
        print("✅ Successfully imported DomainExpertAgent")
    except Exception as e:
        print(f"❌ Failed to import DomainExpertAgent: {e}")
        return False
    
    # Test that the class exists and has the expected methods
    try:
        # Check if the class has the updated method signature
        import inspect
        
        # Get the method signature without instantiating the class
        method_sig = inspect.signature(DomainExpertAgent.provide_knowledge)
        print(f"✅ Method signature: {method_sig}")
        
        # Check return type annotation
        return_type = method_sig.return_annotation
        print(f"✅ Return type: {return_type}")
        
        if return_type == AgentResponse:
            print("✅ Return type is correctly AgentResponse")
        else:
            print("❌ Return type should be AgentResponse")
            return False
            
    except Exception as e:
        print(f"❌ Failed to check method signature: {e}")
        return False
    
    # Test that helper methods are defined in the class
    helper_methods = [
        "_convert_to_agent_response",
        "_calculate_enhancement_metrics", 
        "_extract_cognitive_flags",
        "_convert_cognitive_flags"
    ]
    
    for method in helper_methods:
        if hasattr(DomainExpertAgent, method):
            print(f"✅ Helper method exists: {method}")
        else:
            print(f"❌ Missing helper method: {method}")
            return False
    
    print("\n✅ DomainExpertAgent structure test completed successfully!")
    return True

if __name__ == "__main__":
    success = test_domain_expert_structure()
    if success:
        print("\n🎉 DomainExpertAgent update is working correctly!")
    else:
        print("\n❌ DomainExpertAgent update has issues!") 