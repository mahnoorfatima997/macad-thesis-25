#!/usr/bin/env python3
"""
Evidence-Based Routing System Analysis
Comprehensive testing with real user inputs to verify routing accuracy
"""

import sys
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, 'thesis-agents')

class RoutingAnalyzer:
    def __init__(self):
        self.test_cases = [
            # Design Problem Cases (should NOT trigger gamification)
            {
                "input": "Hmm, well the main goal is to turn this big, old warehouse into a real 'go-to' spot for the neighborhood — somewhere people can come for events, classes, sports, or just to hang out. I'm imagining: A big flexible hall for markets, concerts, and community dinners. Smaller rooms for workshops, meetings, or after-school activities. A café that kind of 'spills' into the main space so it always feels alive. Maybe even an indoor garden or green wall to balance out the industrial vibe. The users? Pretty much everyone — kids after school, parents meeting friends, seniors looking for a place to socialize. I want spaces where people can bump into each other naturally instead of being in totally separate zones. The most important function is flexibility — being able to reconfigure spaces quickly without them feeling empty or awkward. What I'm still figuring out is how to organize it all so it doesn't feel like a maze but also doesn't turn into one giant echo chamber.",
                "expected_route": "balanced_guidance",
                "expected_classification": "design_problem",
                "should_gamify": False,
                "description": "User's actual warehouse community center description"
            },
            {
                "input": "I'm working on a residential project and trying to figure out how to balance privacy with community interaction in the courtyard spaces.",
                "expected_route": "balanced_guidance",
                "expected_classification": "design_problem",
                "should_gamify": False,
                "description": "Design problem with specific challenge"
            },
            {
                "input": "My museum design needs to handle different visitor flows - families, school groups, and individual visitors. How should I organize the circulation?",
                "expected_route": "balanced_guidance", 
                "expected_classification": "design_problem",
                "should_gamify": False,
                "description": "Design problem seeking guidance"
            },
            
            # Overconfident Cases (SHOULD trigger gamification)
            {
                "input": "This design is perfect and will work for everyone.",
                "expected_route": "cognitive_challenge",
                "expected_classification": "overconfident_statement",
                "should_gamify": True,
                "description": "Clear overconfident statement"
            },
            {
                "input": "My solution is flawless and addresses all possible needs.",
                "expected_route": "cognitive_challenge",
                "expected_classification": "overconfident_statement", 
                "should_gamify": True,
                "description": "Overconfident claim about solution"
            },
            
            # Technical Questions (should route to knowledge, not gamification)
            {
                "input": "What are the ADA requirements for ramp slopes?",
                "expected_route": "knowledge_only",
                "expected_classification": "technical_question",
                "should_gamify": False,
                "description": "Specific technical/code question"
            },
            {
                "input": "How do I calculate the structural load for this beam?",
                "expected_route": "knowledge_only",
                "expected_classification": "technical_question",
                "should_gamify": False,
                "description": "Engineering calculation question"
            },
            
            # Knowledge Requests (should route to knowledge_only)
            {
                "input": "Tell me about passive cooling strategies for hot climates.",
                "expected_route": "knowledge_only",
                "expected_classification": "knowledge_request",
                "should_gamify": False,
                "description": "Knowledge request about strategies"
            },
            {
                "input": "What are some examples of successful community centers?",
                "expected_route": "knowledge_only",
                "expected_classification": "example_request",
                "should_gamify": False,
                "description": "Example request"
            },
            
            # Confusion/Help Cases (should route to socratic)
            {
                "input": "I don't understand how to approach spatial hierarchy in my design.",
                "expected_route": "socratic_clarification",
                "expected_classification": "confusion_expression",
                "should_gamify": False,
                "description": "Confusion about design concept"
            }
        ]
        
        self.results = []
        
    async def test_direct_routing(self):
        """Test routing decision tree directly"""
        print('🧭 TESTING DIRECT ROUTING DECISION TREE')
        print('=' * 80)
        
        try:
            from utils.routing_decision_tree import AdvancedRoutingDecisionTree, RoutingContext
            
            router = AdvancedRoutingDecisionTree()
            
            for i, test_case in enumerate(self.test_cases):
                print(f'\n📋 Test Case {i+1}: {test_case["description"]}')
                print(f'Input: {test_case["input"][:100]}...')
                
                classification = {'user_input': test_case["input"]}
                context = RoutingContext(
                    classification=classification,
                    context_analysis={},
                    routing_suggestions={}
                )
                decision = router.decide_route(context)
                
                # Analyze results
                actual_route = decision.route.value
                actual_intent = decision.user_intent
                expected_route = test_case["expected_route"]
                expected_classification = test_case["expected_classification"]
                
                route_correct = actual_route == expected_route
                classification_reasonable = actual_intent in [expected_classification, "implementation_request", "general_statement"]
                
                result = {
                    "test_case": i+1,
                    "description": test_case["description"],
                    "input_preview": test_case["input"][:50] + "...",
                    "expected_route": expected_route,
                    "actual_route": actual_route,
                    "expected_classification": expected_classification,
                    "actual_intent": actual_intent,
                    "route_correct": route_correct,
                    "classification_reasonable": classification_reasonable,
                    "should_gamify": test_case["should_gamify"],
                    "metadata": decision.metadata
                }
                
                self.results.append(result)
                
                print(f'Expected route: {expected_route}')
                print(f'Actual route: {actual_route}')
                print(f'Expected classification: {expected_classification}')
                print(f'Actual intent: {actual_intent}')
                print(f'Route correct: {"✅" if route_correct else "❌"}')
                print(f'Classification reasonable: {"✅" if classification_reasonable else "❌"}')
                
            return True
            
        except Exception as e:
            print(f'❌ Direct routing test failed: {e}')
            import traceback
            traceback.print_exc()
            return False

    async def test_context_agent_classification(self):
        """Test context agent classification for each case"""
        print('\n🎯 TESTING CONTEXT AGENT CLASSIFICATION')
        print('=' * 80)

        try:
            from agents.context_agent import ContextAgent
            from state_manager import ArchMentorState

            agent = ContextAgent()

            for i, test_case in enumerate(self.test_cases):
                print(f'\n📋 Context Agent Test {i+1}: {test_case["description"]}')

                state = ArchMentorState()
                # Add conversation context to avoid first_message issues
                state.messages = [
                    {"role": "user", "content": "I'm working on an architecture project"},
                    {"role": "assistant", "content": "Great! Tell me more about it."},
                    {"role": "user", "content": test_case["input"]}
                ]

                result = await agent.analyze_student_input(state, test_case["input"])

                if hasattr(result, 'metadata') and result.metadata:
                    classification = result.metadata.get('core_classification', {})

                    interaction_type = classification.get('interaction_type', 'unknown')
                    is_technical = classification.get('is_technical_question', False)
                    confidence_level = classification.get('confidence_level', 'unknown')

                    print(f'Interaction type: {interaction_type}')
                    print(f'Is technical question: {is_technical}')
                    print(f'Confidence level: {confidence_level}')

                    # Update results
                    if i < len(self.results):
                        self.results[i]['context_agent_type'] = interaction_type
                        self.results[i]['context_agent_technical'] = is_technical
                        self.results[i]['context_agent_confidence'] = confidence_level
                else:
                    print('❌ No classification data found')

            return True

        except Exception as e:
            print(f'❌ Context agent test failed: {e}')
            import traceback
            traceback.print_exc()
            return False

    async def test_complete_workflow(self):
        """Test complete workflow for critical cases"""
        print('\n🔄 TESTING COMPLETE WORKFLOW')
        print('=' * 80)

        try:
            from orchestration.langgraph_orchestrator import LangGraphOrchestrator
            from state_manager import ArchMentorState

            orchestrator = LangGraphOrchestrator()

            # Test a few critical cases
            critical_cases = [0, 3, 5]  # Design problem, overconfident, technical question

            for case_idx in critical_cases:
                if case_idx >= len(self.test_cases):
                    continue

                test_case = self.test_cases[case_idx]
                print(f'\n📋 Workflow Test: {test_case["description"]}')

                state = ArchMentorState()
                state.messages = [
                    {"role": "user", "content": "I'm working on an architecture project"},
                    {"role": "assistant", "content": "Great! Tell me more about it."},
                    {"role": "user", "content": test_case["input"]}
                ]

                result = await orchestrator.process_student_input(state)

                if isinstance(result, dict):
                    metadata = result.get('response_metadata', result.get('metadata', {}))
                    routing_path = metadata.get('routing_path', 'unknown')
                    agents_used = metadata.get('agents_used', [])
                    gamification = metadata.get('gamification', {})

                    print(f'Routing path: {routing_path}')
                    print(f'Agents used: {agents_used}')
                    print(f'Has gamification: {bool(gamification)}')

                    # Update results
                    if case_idx < len(self.results):
                        self.results[case_idx]['workflow_route'] = routing_path
                        self.results[case_idx]['workflow_agents'] = agents_used
                        self.results[case_idx]['workflow_gamification'] = bool(gamification)

            return True

        except Exception as e:
            print(f'❌ Workflow test failed: {e}')
            import traceback
            traceback.print_exc()
            return False

    def generate_analysis_report(self):
        """Generate comprehensive analysis report"""
        print('\n📊 COMPREHENSIVE ROUTING ANALYSIS REPORT')
        print('=' * 100)

        total_tests = len(self.results)
        route_correct_count = sum(1 for r in self.results if r.get('route_correct', False))
        classification_reasonable_count = sum(1 for r in self.results if r.get('classification_reasonable', False))

        print(f'Total test cases: {total_tests}')
        print(f'Route accuracy: {route_correct_count}/{total_tests} ({route_correct_count/total_tests*100:.1f}%)')
        print(f'Classification reasonable: {classification_reasonable_count}/{total_tests} ({classification_reasonable_count/total_tests*100:.1f}%)')

        print('\n📋 DETAILED RESULTS:')
        print('-' * 100)

        for result in self.results:
            print(f'\n🧪 Test {result["test_case"]}: {result["description"]}')
            print(f'   Input: {result["input_preview"]}')
            print(f'   Expected route: {result["expected_route"]} | Actual: {result["actual_route"]} | {"✅" if result["route_correct"] else "❌"}')
            print(f'   Expected class: {result["expected_classification"]} | Actual: {result["actual_intent"]} | {"✅" if result["classification_reasonable"] else "❌"}')

            if 'context_agent_type' in result:
                print(f'   Context agent: {result["context_agent_type"]} | Technical: {result["context_agent_technical"]}')

            if 'workflow_route' in result:
                print(f'   Workflow route: {result["workflow_route"]} | Gamification: {result["workflow_gamification"]}')

        print('\n🎯 CRITICAL ISSUES IDENTIFIED:')
        issues = []

        for result in self.results:
            if not result['route_correct']:
                issues.append(f"❌ Test {result['test_case']}: Expected {result['expected_route']}, got {result['actual_route']}")

            if result['should_gamify'] and result.get('workflow_gamification') == False:
                issues.append(f"⚠️ Test {result['test_case']}: Should gamify but doesn't")

            if not result['should_gamify'] and result.get('workflow_gamification') == True:
                issues.append(f"⚠️ Test {result['test_case']}: Shouldn't gamify but does")

        if issues:
            for issue in issues:
                print(issue)
        else:
            print('✅ No critical issues found')

        return len(issues) == 0

async def main():
    """Run comprehensive routing analysis"""
    print('🚀 EVIDENCE-BASED ROUTING SYSTEM ANALYSIS')
    print('=' * 100)
    print('Testing with real user inputs to verify routing accuracy')

    analyzer = RoutingAnalyzer()

    # Run all tests
    direct_routing_success = await analyzer.test_direct_routing()
    context_agent_success = await analyzer.test_context_agent_classification()
    workflow_success = await analyzer.test_complete_workflow()

    # Generate comprehensive report
    no_critical_issues = analyzer.generate_analysis_report()

    print('\n🏁 FINAL ANALYSIS CONCLUSION')
    print('=' * 100)

    if direct_routing_success and context_agent_success and workflow_success and no_critical_issues:
        print('✅ ROUTING SYSTEM IS WORKING CORRECTLY')
        print('All test cases pass with expected behavior')
    else:
        print('❌ ROUTING SYSTEM HAS ISSUES')
        print('Critical problems identified that need fixing')

        if not direct_routing_success:
            print('  - Direct routing decision tree has problems')
        if not context_agent_success:
            print('  - Context agent classification has problems')
        if not workflow_success:
            print('  - Complete workflow has problems')
        if not no_critical_issues:
            print('  - Critical routing/gamification issues found')

    return direct_routing_success and context_agent_success and workflow_success and no_critical_issues

if __name__ == "__main__":
    asyncio.run(main())
