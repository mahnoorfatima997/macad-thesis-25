#!/usr/bin/env python3
"""
Test script to check if utils module and AgentResponse are accessible
"""

import sys
import os

# Add the thesis-agents directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'thesis-agents'))

try:
    from utils.agent_response import AgentResponse, ResponseType, CognitiveFlag, ResponseBuilder, EnhancementMetrics
    print("✅ Successfully imported AgentResponse and related classes")
    
    # Test creating a simple response
    response = ResponseBuilder.create_analysis_response(
        response_text="Test response",
        cognitive_flags=[],
        enhancement_metrics=EnhancementMetrics(),
        agent_name="test_agent"
    )
    
    print(f"✅ Successfully created AgentResponse: {type(response)}")
    print(f"   Response type: {response.response_type}")
    print(f"   Agent name: {response.agent_name}")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Current sys.path:")
    for path in sys.path:
        print(f"   {path}")
except Exception as e:
    print(f"❌ Other error: {e}")

print("\nChecking if utils directory exists:")
utils_path = os.path.join(os.path.dirname(__file__), 'thesis-agents', 'utils')
print(f"Utils path: {utils_path}")
print(f"Utils directory exists: {os.path.exists(utils_path)}")

if os.path.exists(utils_path):
    print("Utils directory contents:")
    for file in os.listdir(utils_path):
        print(f"   {file}") 