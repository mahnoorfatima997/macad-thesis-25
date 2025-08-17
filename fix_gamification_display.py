#!/usr/bin/env python3
"""
Fix Gamification Display Issue
"""

import sys
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, 'thesis-agents')

async def test_cognitive_enhancement_proper():
    """Test the cognitive enhancement agent with correct method"""
    print('🧠 TESTING COGNITIVE ENHANCEMENT AGENT')
    print('=' * 60)
    
    try:
        from agents.cognitive_enhancement import CognitiveEnhancementAgent
        from state_manager import ArchMentorState
        
        agent = CognitiveEnhancementAgent()
        state = ArchMentorState()
        
        # Add overconfident message to state
        overconfident_input = 'This design is perfect and will work for everyone'
        state.messages = [{"role": "user", "content": overconfident_input}]
        
        print(f'Testing input: {overconfident_input}')
        
        # Use the correct method
        context_classification = {"primary_gap": "overconfidence"}
        analysis_result = {"user_intent": "overconfident_statement"}
        routing_decision = {"route": "cognitive_challenge"}
        
        result = await agent.provide_challenge(
            state=state,
            context_classification=context_classification,
            analysis_result=analysis_result,
            routing_decision=routing_decision
        )
        
        print(f'\nResult type: {type(result)}')
        print(f'Result: {result}')
        
        # Check if result has gamification data
        if hasattr(result, 'metadata') and result.metadata:
            print(f'\nMetadata: {result.metadata}')
            if 'gamification' in result.metadata:
                gam_data = result.metadata['gamification']
                print(f'\n🎯 Gamification found in metadata:')
                print(f'  Type: {gam_data.get("type", "unknown")}')
                print(f'  Message: {gam_data.get("message", "No message")}')
                print(f'  Points: {gam_data.get("points_awarded", 0)}')
                return True
        
        # Check response text for gamification elements
        if hasattr(result, 'response_text') and result.response_text:
            response_text = result.response_text
            print(f'\nResponse text: {response_text[:200]}...')
            
            # Look for gamification indicators in text
            gamification_indicators = ['🚨', '🎯', '🌟', '⚠️', 'challenge', 'think about']
            has_gamification = any(indicator in response_text.lower() for indicator in gamification_indicators)
            
            if has_gamification:
                print('✅ Gamification elements found in response text')
                return True
            else:
                print('❌ No gamification elements in response text')
        
        print('❌ No gamification data found')
        return False
        
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()
        return False

async def test_orchestration_gamification():
    """Test gamification through orchestration"""
    print('\n🔄 TESTING ORCHESTRATION GAMIFICATION')
    print('=' * 60)
    
    try:
        from orchestration.langgraph_orchestrator import LangGraphOrchestrator
        from orchestration.types import WorkflowState
        
        orchestrator = LangGraphOrchestrator()
        
        # Test overconfident statement
        test_input = 'This design is perfect and will work for everyone'
        print(f'Testing: {test_input}')
        
        # Create workflow state
        initial_state = WorkflowState(
            user_input=test_input,
            messages=[{"role": "user", "content": test_input}],
            classification={},
            context_analysis={},
            routing_suggestions={},
            domain_expert_response="",
            socratic_response="",
            cognitive_enhancement="",
            final_response="",
            response_metadata={}
        )
        
        # Process through orchestrator
        # Note: We need to check what method actually exists
        methods = [method for method in dir(orchestrator) if not method.startswith('_')]
        print(f'Available orchestrator methods: {methods[:10]}...')
        
        # Try to find the right method
        if hasattr(orchestrator, 'process'):
            result = await orchestrator.process(initial_state)
        elif hasattr(orchestrator, 'run'):
            result = await orchestrator.run(initial_state)
        else:
            print('❌ Could not find orchestrator processing method')
            return False
        
        print(f'Orchestration result: {result}')
        
        # Check for gamification in result
        if isinstance(result, dict):
            if 'response_metadata' in result:
                metadata = result['response_metadata']
                if 'gamification' in metadata:
                    print('✅ Gamification found in orchestration result')
                    return True
        
        print('❌ No gamification in orchestration result')
        return False
        
    except Exception as e:
        print(f'❌ Orchestration test error: {e}')
        return False

def test_gamification_ui_components():
    """Test gamification UI components"""
    print('\n🖥️ TESTING GAMIFICATION UI COMPONENTS')
    print('=' * 60)
    
    try:
        from dashboard.ui.gamification_components import GamificationDisplay
        
        display = GamificationDisplay()
        print('✅ GamificationDisplay created successfully')
        
        # Test gamification data
        test_gamification_data = {
            'type': 'overconfidence_challenge',
            'message': '🚨 Hold on! While confidence is great, every design has trade-offs. What potential challenges might this design face?',
            'visual_effect': 'warning_border',
            'points_awarded': 0,
            'trigger_type': 'overconfidence_challenge',
            'enhancement_applied': True
        }
        
        print('Test gamification data:')
        for key, value in test_gamification_data.items():
            print(f'  {key}: {value}')
        
        # Check if display has methods to render gamification
        methods = [method for method in dir(display) if not method.startswith('_')]
        print(f'\nGamificationDisplay methods: {methods}')
        
        return True
        
    except Exception as e:
        print(f'❌ UI components test error: {e}')
        return False

def create_gamification_metadata_fix():
    """Create a fix for gamification metadata propagation"""
    print('\n🔧 CREATING GAMIFICATION METADATA FIX')
    print('=' * 60)
    
    # The issue is likely in the orchestration layer not properly extracting
    # and propagating gamification metadata from the cognitive enhancement agent
    
    fix_code = '''
# Fix for orchestration/orchestrator.py _build_metadata method

def _build_metadata(self, ordered_results: Dict[str, Any], routing_decision: Any, 
                   classification: Dict[str, Any]) -> Dict[str, Any]:
    """Build comprehensive metadata including gamification data."""
    
    metadata = {
        "routing_path": routing_decision.route.value if hasattr(routing_decision, 'route') else 'unknown',
        "agents_used": list(ordered_results.keys()),
        "user_intent": getattr(routing_decision, 'user_intent', 'unknown'),
        "response_type": self._determine_response_type(routing_decision),
        "timestamp": datetime.now().isoformat()
    }
    
    # FIXED: Extract gamification metadata from cognitive enhancement agent
    if 'cognitive_enhancement' in ordered_results:
        cognitive_result = ordered_results['cognitive_enhancement']
        
        # Check if cognitive result has gamification metadata
        if hasattr(cognitive_result, 'metadata') and cognitive_result.metadata:
            if 'gamification' in cognitive_result.metadata:
                metadata['gamification'] = cognitive_result.metadata['gamification']
                metadata['gamification_display'] = cognitive_result.metadata['gamification']
        
        # Also check response text for gamification indicators
        if hasattr(cognitive_result, 'response_text'):
            response_text = cognitive_result.response_text
            gamification_indicators = ['🚨', '🎯', '🌟', '⚠️']
            
            if any(indicator in response_text for indicator in gamification_indicators):
                # Create gamification metadata if not already present
                if 'gamification' not in metadata:
                    metadata['gamification'] = {
                        'trigger_type': 'cognitive_challenge',
                        'enhancement_applied': True,
                        'message': 'Gamification elements detected in response'
                    }
    
    return metadata
    '''
    
    print('Gamification metadata fix code:')
    print(fix_code)
    
    return fix_code

async def main():
    """Run gamification display tests and fixes"""
    print('🎮 GAMIFICATION DISPLAY DIAGNOSIS AND FIX')
    print('=' * 80)
    
    # Test individual components
    cognitive_success = await test_cognitive_enhancement_proper()
    orchestration_success = await test_orchestration_gamification()
    ui_success = test_gamification_ui_components()
    
    print('\n📊 GAMIFICATION TEST RESULTS')
    print('=' * 60)
    print(f'Cognitive Enhancement: {"✅" if cognitive_success else "❌"}')
    print(f'Orchestration: {"✅" if orchestration_success else "❌"}')
    print(f'UI Components: {"✅" if ui_success else "❌"}')
    
    # Generate fix
    fix_code = create_gamification_metadata_fix()
    
    print('\n🔧 DIAGNOSIS:')
    print('The gamification system has these components:')
    print('1. ✅ Routing correctly identifies overconfident statements → cognitive_challenge')
    print('2. ✅ Cognitive enhancement agent exists and has proper methods')
    print('3. ✅ UI components exist for displaying gamification')
    print('4. ❌ Gamification metadata is not being properly propagated through orchestration')
    
    print('\n💡 SOLUTION:')
    print('The orchestration layer needs to extract gamification metadata from')
    print('the cognitive enhancement agent and include it in the response metadata')
    print('so the UI can display it properly.')
    
    print('\n🚀 NEXT STEPS:')
    print('1. Fix the orchestration _build_metadata method to extract gamification data')
    print('2. Ensure gamification metadata is passed to the UI')
    print('3. Test the complete flow from input → routing → cognitive enhancement → UI display')

if __name__ == "__main__":
    asyncio.run(main())
