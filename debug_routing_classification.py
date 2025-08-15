#!/usr/bin/env python3
"""
Debug Routing Classification Issue
"""

import sys
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, 'thesis-agents')

async def test_routing_classification():
    """Test routing classification for the user's input"""
    print('🧭 DEBUGGING ROUTING CLASSIFICATION')
    print('=' * 80)
    
    user_input = """Hmm, well the main goal is to turn this big, old warehouse into a real "go-to" spot for the neighborhood — somewhere people can come for events, classes, sports, or just to hang out.

I'm imagining:

A big flexible hall for markets, concerts, and community dinners.

Smaller rooms for workshops, meetings, or after-school activities.

A café that kind of "spills" into the main space so it always feels alive.

Maybe even an indoor garden or green wall to balance out the industrial vibe.

The users? Pretty much everyone — kids after school, parents meeting friends, seniors looking for a place to socialize. I want spaces where people can bump into each other naturally instead of being in totally separate zones.

The most important function is flexibility — being able to reconfigure spaces quickly without them feeling empty or awkward.

What I'm still figuring out is how to organize it all so it doesn't feel like a maze but also doesn't turn into one giant echo chamber."""
    
    print(f'User input length: {len(user_input)} characters')
    print(f'Input preview: {user_input[:200]}...')
    
    try:
        from utils.routing_decision_tree import AdvancedRoutingDecisionTree, RoutingContext
        
        router = AdvancedRoutingDecisionTree()
        
        # Test direct routing
        print(f'\n🎯 TESTING DIRECT ROUTING:')
        classification = {'user_input': user_input}
        context = RoutingContext(
            classification=classification,
            context_analysis={},
            routing_suggestions={}
        )
        decision = router.decide_route(context)
        
        print(f'Route: {decision.route.value}')
        print(f'Intent: {decision.user_intent}')
        print(f'Rule: {decision.rule_applied}')
        print(f'Metadata: {decision.metadata}')
        
        # Analyze why this might be classified as technical
        print(f'\n🔍 ANALYZING CLASSIFICATION:')
        
        # Check for technical keywords
        technical_keywords = ['technical', 'how to', 'what is', 'explain', 'define']
        found_technical = [kw for kw in technical_keywords if kw in user_input.lower()]
        print(f'Technical keywords found: {found_technical}')
        
        # Check for question patterns
        questions = [line for line in user_input.split('.') if '?' in line]
        print(f'Questions found: {len(questions)}')
        for q in questions:
            print(f'  - {q.strip()}')
        
        # Check for overconfidence patterns
        confidence_words = ['perfect', 'definitely', 'always', 'never', 'best', 'worst', 'impossible']
        found_confidence = [cw for cw in confidence_words if cw in user_input.lower()]
        print(f'Overconfidence words: {found_confidence}')
        
        # Check for uncertainty patterns (should prevent gamification)
        uncertainty_words = ['figuring out', 'not sure', 'wondering', 'maybe', 'might', 'could']
        found_uncertainty = [uw for uw in uncertainty_words if uw in user_input.lower()]
        print(f'Uncertainty words: {found_uncertainty}')
        
        print(f'\n📊 CLASSIFICATION ANALYSIS:')
        print(f'Should be technical question: {"❌ NO" if not found_technical else "⚠️ MAYBE"}')
        print(f'Should trigger gamification: {"❌ NO" if found_uncertainty else "⚠️ MAYBE"}')
        print(f'Expected route: balanced_guidance or socratic_exploration')
        print(f'Actual route: {decision.route.value}')
        
        if decision.route.value in ['knowledge_with_challenge', 'cognitive_challenge']:
            print(f'\n⚠️ ROUTING ISSUE DETECTED!')
            print(f'This input should NOT trigger gamification or challenge modes.')
            return False
        else:
            print(f'\n✅ Routing looks correct')
            return True
            
    except Exception as e:
        print(f'❌ Routing test failed: {e}')
        import traceback
        traceback.print_exc()
        return False

async def test_context_agent_classification():
    """Test how the context agent classifies this input"""
    print('\n🎯 TESTING CONTEXT AGENT CLASSIFICATION')
    print('=' * 80)
    
    try:
        from agents.context_agent import ContextAgent
        from state_manager import ArchMentorState
        
        agent = ContextAgent()
        state = ArchMentorState()
        
        user_input = """Hmm, well the main goal is to turn this big, old warehouse into a real "go-to" spot for the neighborhood — somewhere people can come for events, classes, sports, or just to hang out.

I'm imagining:

A big flexible hall for markets, concerts, and community dinners.

Smaller rooms for workshops, meetings, or after-school activities.

A café that kind of "spills" into the main space so it always feels alive.

Maybe even an indoor garden or green wall to balance out the industrial vibe.

The users? Pretty much everyone — kids after school, parents meeting friends, seniors looking for a place to socialize. I want spaces where people can bump into each other naturally instead of being in totally separate zones.

The most important function is flexibility — being able to reconfigure spaces quickly without them feeling empty or awkward.

What I'm still figuring out is how to organize it all so it doesn't feel like a maze but also doesn't turn into one giant echo chamber."""
        
        # Add some conversation context
        state.messages = [
            {"role": "user", "content": "I'm working on a community center design"},
            {"role": "assistant", "content": "That's great! What aspects are you considering?"},
            {"role": "user", "content": user_input}
        ]
        
        print(f'Testing context agent classification...')
        
        result = await agent.analyze_student_input(state, user_input)
        
        print(f'Context agent result type: {type(result)}')

        # Check if result has metadata with core_classification
        if hasattr(result, 'metadata') and result.metadata:
            core_classification = result.metadata.get('core_classification', {})
            if core_classification:
                classification = core_classification
            print(f'\n📋 CLASSIFICATION RESULTS:')
            print(f'Interaction type: {classification.get("interaction_type", "unknown")}')
            print(f'Understanding level: {classification.get("understanding_level", "unknown")}')
            print(f'Confidence level: {classification.get("confidence_level", "unknown")}')
            print(f'Engagement level: {classification.get("engagement_level", "unknown")}')
            print(f'User intent: {classification.get("user_intent", "unknown")}')
            print(f'Is technical question: {classification.get("is_technical_question", False)}')
            print(f'Is pure knowledge request: {classification.get("is_pure_knowledge_request", False)}')
            
            # Check if this explains the routing issue
            if classification.get("is_technical_question", False):
                print(f'\n⚠️ CONTEXT AGENT ISSUE: Incorrectly classified as technical question')
                return False
            elif classification.get("interaction_type") == "technical_question":
                print(f'\n⚠️ CONTEXT AGENT ISSUE: Interaction type incorrectly set to technical_question')
                return False
            else:
                print(f'\n✅ Context agent classification looks reasonable')
                return True
        else:
            print(f'❌ No classification found in result')
            return False
            
    except Exception as e:
        print(f'❌ Context agent test failed: {e}')
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Debug routing classification issue"""
    print('🚀 ROUTING CLASSIFICATION DEBUG')
    print('=' * 100)
    
    # Test direct routing
    routing_success = await test_routing_classification()
    
    # Test context agent
    context_success = await test_context_agent_classification()
    
    print('\n📊 ROUTING DEBUG RESULTS')
    print('=' * 80)
    print(f'Direct Routing: {"✅ CORRECT" if routing_success else "❌ INCORRECT"}')
    print(f'Context Agent: {"✅ CORRECT" if context_success else "❌ INCORRECT"}')
    
    if not routing_success or not context_success:
        print('\n🔧 ROUTING ISSUE IDENTIFIED!')
        print('=' * 80)
        print('The user\'s thoughtful design description is being misclassified.')
        print('This input should route to:')
        print('  - balanced_guidance (for design guidance)')
        print('  - socratic_exploration (for thoughtful questioning)')
        print('NOT to:')
        print('  - knowledge_with_challenge')
        print('  - cognitive_challenge')
        print('  - technical_question routes')
        print()
        print('The gamification is triggering incorrectly because the')
        print('routing system thinks this is a technical question that')
        print('needs cognitive enhancement, when it\'s actually a')
        print('thoughtful design exploration.')
    else:
        print('\n✅ ROUTING WORKING CORRECTLY')
        print('The issue might be elsewhere in the pipeline.')
    
    return routing_success and context_success

if __name__ == "__main__":
    asyncio.run(main())
