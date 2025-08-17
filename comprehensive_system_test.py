#!/usr/bin/env python3
"""
Comprehensive test of routing, interaction classification, and response quality
"""

import sys
import os
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

sys.path.insert(0, 'thesis-agents')

from agents.context_agent.processors.input_classification import InputClassificationProcessor
from utils.routing_decision_tree import AdvancedRoutingDecisionTree, RoutingContext
from state_manager import ArchMentorState

async def test_ai_classification():
    """Test AI-based interaction classification"""
    print("🤖 TESTING AI INTERACTION CLASSIFICATION")
    print("=" * 80)
    
    processor = InputClassificationProcessor()
    state = ArchMentorState()
    
    test_cases = [
        # Design guidance cases
        'I need help organizing spaces for different age groups in my community center.',
        'How should I handle circulation patterns in a large community space?',
        'I want to create flexible spaces that can change function throughout the day.',
        'help',
        
        # Knowledge only cases  
        'What are some examples of successful community centers in hot climates?',
        'Can you tell me about passive cooling strategies for large buildings?',
        'Can you show me some examples of warehouse-to-community center conversions?',
        
        # Confusion cases
        'I don\'t understand what you mean by spatial hierarchy.',
        'Can you explain that differently? I\'m not following.',
        
        # Edge cases
        'Why do you think natural lighting is important in community spaces?',
        'What factors should I consider when choosing materials?',
    ]
    
    results = []
    
    for test_input in test_cases:
        print(f"\n📝 Input: {test_input}")
        try:
            classification_obj = await processor.perform_core_classification(test_input, state)

            # Extract data from CoreClassification object
            classification = {
                'interaction_type': classification_obj.interaction_type.value if hasattr(classification_obj.interaction_type, 'value') else str(classification_obj.interaction_type),
                'confidence_level': classification_obj.confidence_level.value if hasattr(classification_obj.confidence_level, 'value') else str(classification_obj.confidence_level),
                'understanding_level': classification_obj.understanding_level.value if hasattr(classification_obj.understanding_level, 'value') else str(classification_obj.understanding_level),
                'engagement_level': classification_obj.engagement_level.value if hasattr(classification_obj.engagement_level, 'value') else str(classification_obj.engagement_level),
                'is_technical_question': getattr(classification_obj, 'is_technical_question', False),
                'is_feedback_request': getattr(classification_obj, 'is_feedback_request', False),
                'confidence_score': getattr(classification_obj, 'confidence_score', 0.0),
                'user_input': test_input
            }

            print(f"   🎯 AI Classification: {classification['interaction_type']}")
            print(f"   🤔 Confidence: {classification['confidence_level']}")
            print(f"   📚 Understanding: {classification['understanding_level']}")
            print(f"   🔥 Engagement: {classification['engagement_level']}")
            print(f"   📋 Is Technical: {classification['is_technical_question']}")
            print(f"   🎯 Is Feedback Request: {classification['is_feedback_request']}")
            print(f"   📊 Confidence Score: {classification['confidence_score']}")
            
            results.append({
                'input': test_input,
                'classification': classification
            })
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results.append({
                'input': test_input,
                'error': str(e)
            })
    
    return results

async def test_routing_with_ai_classification(classification_results):
    """Test routing using AI classification results"""
    print("\n🧭 TESTING ROUTING WITH AI CLASSIFICATION")
    print("=" * 80)
    
    router = AdvancedRoutingDecisionTree()
    routing_results = []
    
    for result in classification_results:
        if 'error' in result:
            continue
            
        test_input = result['input']
        classification = result['classification']
        
        print(f"\n📝 Input: {test_input[:60]}...")
        
        # Test routing with AI classification
        context = RoutingContext(
            classification=classification, 
            context_analysis={}, 
            routing_suggestions={}
        )
        decision = router.decide_route(context)
        
        print(f"   🛤️  Route: {decision.route.value}")
        print(f"   🎯 Intent: {decision.user_intent}")
        print(f"   📏 Rule: {decision.rule_applied}")
        print(f"   🔍 Pure Knowledge: {decision.metadata.get('is_pure_knowledge_request', 'N/A')}")
        print(f"   🤖 AI vs Pattern Intent: {classification['interaction_type']} vs {decision.user_intent}")

        routing_results.append({
            'input': test_input,
            'ai_classification': classification['interaction_type'],
            'routing_intent': decision.user_intent,
            'route': decision.route.value,
            'rule': decision.rule_applied,
            'confidence_score': classification['confidence_score']
        })
    
    return routing_results

def analyze_classification_consistency(routing_results):
    """Analyze consistency between AI classification and routing decisions"""
    print("\n📊 ANALYZING CLASSIFICATION CONSISTENCY")
    print("=" * 80)
    
    inconsistencies = []
    
    for result in routing_results:
        ai_class = result['ai_classification']
        routing_intent = result['routing_intent']
        
        # Check for logical inconsistencies
        is_inconsistent = False
        reason = ""
        
        # Map AI classification to expected routing patterns
        expected_routing_map = {
            'design_problem': ['design_guidance', 'design_exploration', 'implementation_request'],
            'example_request': ['example_request', 'knowledge_request'],
            'knowledge_seeking': ['knowledge_request', 'design_guidance'],
            'confusion_expression': ['confusion_expression', 'clarification_request'],
            'feedback_request': ['feedback_request', 'evaluation_request']
        }

        expected_routes = expected_routing_map.get(ai_class, [])
        if expected_routes and routing_intent not in expected_routes:
            is_inconsistent = True
            reason = f"AI classified as '{ai_class}' but routed as '{routing_intent}' (expected: {expected_routes})"
        
        if is_inconsistent:
            inconsistencies.append({
                'input': result['input'],
                'ai_classification': ai_class,
                'routing_intent': routing_intent,
                'route': result['route'],
                'reason': reason,
                'confidence_score': result['confidence_score']
            })
            print(f"❌ INCONSISTENCY: {result['input'][:50]}...")
            print(f"   {reason}")
            print(f"   AI Reasoning: {result['ai_reasoning'][:100]}...")
            print()
    
    if not inconsistencies:
        print("✅ No major inconsistencies found!")
    else:
        print(f"⚠️  Found {len(inconsistencies)} inconsistencies")
    
    return inconsistencies

async def main():
    """Main test function"""
    print("🔍 COMPREHENSIVE SYSTEM ANALYSIS")
    print("=" * 120)
    
    # Test AI classification
    classification_results = await test_ai_classification()
    
    # Test routing with AI classification
    routing_results = await test_routing_with_ai_classification(classification_results)
    
    # Analyze consistency
    inconsistencies = analyze_classification_consistency(routing_results)
    
    # Summary
    print("\n📋 SUMMARY")
    print("=" * 80)
    print(f"📊 Total test cases: {len(classification_results)}")
    print(f"❌ Classification errors: {len([r for r in classification_results if 'error' in r])}")
    print(f"⚠️  Routing inconsistencies: {len(inconsistencies)}")
    
    if inconsistencies:
        print("\n🔧 RECOMMENDATIONS:")
        print("- Improve AI classification prompts")
        print("- Add smarter intent mapping between AI classification and routing")
        print("- Implement hybrid classification approach")
    else:
        print("\n✅ System appears to be working well!")

if __name__ == "__main__":
    asyncio.run(main())
