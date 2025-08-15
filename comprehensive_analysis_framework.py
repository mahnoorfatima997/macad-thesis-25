#!/usr/bin/env python3
"""
Comprehensive Analysis and Testing Framework for Learning Tool Application
"""

import sys
import os
import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass, asdict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

sys.path.insert(0, 'thesis-agents')
sys.path.insert(0, 'dashboard')

@dataclass
class TestResult:
    """Test result data structure"""
    test_name: str
    input_text: str
    expected_route: str
    actual_route: str
    classification: Dict[str, Any]
    response_text: str
    response_metadata: Dict[str, Any]
    success: bool
    notes: str
    timestamp: str

@dataclass
class RouteAnalysis:
    """Route analysis data structure"""
    route_name: str
    description: str
    trigger_conditions: List[str]
    sample_inputs: List[str]
    expected_output_format: str
    agents_used: List[str]
    test_results: List[TestResult]

class ComprehensiveAnalysisFramework:
    """Main analysis framework"""
    
    def __init__(self):
        self.test_results = []
        self.route_analyses = {}
        self.domain_expert_tests = []
        self.gamification_tests = []
        self.end_to_end_tests = []
        
        # Define comprehensive test cases
        self.test_cases = self._define_test_cases()
        
    def _define_test_cases(self) -> Dict[str, List[Dict]]:
        """Define comprehensive test cases for all routes"""
        return {
            "knowledge_only": [
                {
                    "input": "What are some examples of successful community centers in hot climates?",
                    "expected_route": "knowledge_only",
                    "category": "example_request",
                    "notes": "Should provide direct examples without guidance"
                },
                {
                    "input": "Can you tell me about passive cooling strategies for large buildings?",
                    "expected_route": "knowledge_only", 
                    "category": "knowledge_request",
                    "notes": "Pure information request"
                },
                {
                    "input": "What factors should I consider when choosing materials?",
                    "expected_route": "knowledge_only",
                    "category": "knowledge_request", 
                    "notes": "Factual information about material selection"
                },
                {
                    "input": "Show me examples of warehouse-to-community center conversions",
                    "expected_route": "knowledge_only",
                    "category": "example_request",
                    "notes": "Specific project examples"
                }
            ],
            
            "balanced_guidance": [
                {
                    "input": "I need help organizing spaces for different age groups in my community center",
                    "expected_route": "balanced_guidance",
                    "category": "design_guidance",
                    "notes": "Should provide structured guidance with insight/watch/direction"
                },
                {
                    "input": "I want to create flexible spaces that can change function throughout the day",
                    "expected_route": "balanced_guidance", 
                    "category": "design_problem",
                    "notes": "Design challenge requiring guidance"
                },
                {
                    "input": "help",
                    "expected_route": "balanced_guidance",
                    "category": "general_help",
                    "notes": "General help request"
                }
            ],
            
            "socratic_clarification": [
                {
                    "input": "I don't understand what you mean by spatial hierarchy",
                    "expected_route": "socratic_clarification",
                    "category": "confusion_expression", 
                    "notes": "Should provide clarifying questions and explanations"
                },
                {
                    "input": "Can you explain that differently? I'm not following",
                    "expected_route": "socratic_clarification",
                    "category": "clarification_request",
                    "notes": "Request for different explanation approach"
                }
            ],
            
            "socratic_exploration": [
                {
                    "input": "Why do you think natural lighting is important in community spaces?",
                    "expected_route": "socratic_exploration",
                    "category": "exploratory_question",
                    "notes": "Should engage in deeper exploration through questions"
                }
            ],
            
            "multi_agent_comprehensive": [
                {
                    "input": "What do you think about my approach to organizing the entrance area?",
                    "expected_route": "multi_agent_comprehensive",
                    "category": "feedback_request",
                    "notes": "Should provide comprehensive multi-perspective analysis"
                }
            ],
            
            "cognitive_challenge": [
                {
                    "input": "This design is perfect and will definitely work for everyone",
                    "expected_route": "cognitive_challenge", 
                    "category": "overconfident_statement",
                    "notes": "Should challenge overconfidence with reality checks"
                }
            ]
        }
    
    async def run_routing_classification_analysis(self):
        """1. Routing & Classification Analysis"""
        print("🧭 ROUTING & CLASSIFICATION ANALYSIS")
        print("=" * 80)
        
        from utils.routing_decision_tree import AdvancedRoutingDecisionTree, RoutingContext
        from agents.context_agent.processors.input_classification import InputClassificationProcessor
        from state_manager import ArchMentorState
        
        router = AdvancedRoutingDecisionTree()
        classifier = InputClassificationProcessor()
        state = ArchMentorState()
        
        for route_name, test_cases in self.test_cases.items():
            print(f"\n📍 Testing Route: {route_name.upper()}")
            print("-" * 40)
            
            route_results = []
            
            for test_case in test_cases:
                test_input = test_case["input"]
                expected_route = test_case["expected_route"]
                
                try:
                    # Get AI classification
                    ai_classification = await classifier.perform_core_classification(test_input, state)
                    classification_dict = {
                        'interaction_type': ai_classification.interaction_type.value,
                        'confidence_level': ai_classification.confidence_level.value,
                        'understanding_level': ai_classification.understanding_level.value,
                        'engagement_level': ai_classification.engagement_level.value,
                        'user_input': test_input
                    }
                    
                    # Get routing decision
                    context = RoutingContext(
                        classification=classification_dict,
                        context_analysis={},
                        routing_suggestions={}
                    )
                    decision = router.decide_route(context)
                    
                    # Analyze result
                    success = decision.route.value == expected_route
                    
                    result = TestResult(
                        test_name=f"{route_name}_{len(route_results)}",
                        input_text=test_input,
                        expected_route=expected_route,
                        actual_route=decision.route.value,
                        classification=classification_dict,
                        response_text="",  # Will be filled in response analysis
                        response_metadata={},
                        success=success,
                        notes=test_case["notes"],
                        timestamp=datetime.now().isoformat()
                    )
                    
                    route_results.append(result)
                    
                    status = "✅" if success else "❌"
                    print(f"{status} {test_input[:50]}...")
                    print(f"    Expected: {expected_route} | Got: {decision.route.value}")
                    print(f"    AI Classification: {classification_dict['interaction_type']}")
                    print(f"    Rule Applied: {decision.rule_applied}")
                    
                except Exception as e:
                    print(f"❌ Error testing '{test_input[:30]}...': {e}")
                    
            # Calculate route accuracy
            successful = sum(1 for r in route_results if r.success)
            total = len(route_results)
            accuracy = (successful / total * 100) if total > 0 else 0
            
            print(f"\n📊 Route {route_name} Accuracy: {successful}/{total} ({accuracy:.1f}%)")
            
            self.route_analyses[route_name] = RouteAnalysis(
                route_name=route_name,
                description=f"Route for {route_name} interactions",
                trigger_conditions=[],  # Will be filled from routing rules
                sample_inputs=[tc["input"] for tc in test_cases],
                expected_output_format="",  # Will be filled in response analysis
                agents_used=[],  # Will be filled from routing rules
                test_results=route_results
            )
        
        return self.route_analyses
    
    async def run_response_type_analysis(self):
        """2. Response Type Analysis"""
        print("\n🎭 RESPONSE TYPE ANALYSIS")
        print("=" * 80)
        
        from orchestration.orchestrator import ArchMentorOrchestrator
        from state_manager import ArchMentorState
        
        orchestrator = ArchMentorOrchestrator()
        
        # Test different response types
        response_test_cases = [
            {
                "input": "What are examples of community centers in hot climates?",
                "expected_type": "knowledge_only",
                "description": "Should provide direct examples without guidance questions"
            },
            {
                "input": "I need help organizing spaces for different age groups",
                "expected_type": "balanced_guidance", 
                "description": "Should provide Synthesis: format with Insight/Watch/Direction"
            },
            {
                "input": "I don't understand spatial hierarchy",
                "expected_type": "socratic_clarification",
                "description": "Should provide clarifying questions and scaffolding"
            }
        ]
        
        for test_case in response_test_cases:
            print(f"\n🧪 Testing Response Type: {test_case['expected_type']}")
            print(f"Input: {test_case['input']}")
            
            try:
                # Create state with test input
                state = ArchMentorState()
                state.messages = [{"role": "user", "content": test_case["input"]}]
                
                # Process through orchestrator
                result = await orchestrator.process_student_input(state)
                
                response_text = result.get("final_response", "")
                metadata = result.get("response_metadata", {})
                
                print(f"Response Type: {metadata.get('response_type', 'unknown')}")
                print(f"Routing Path: {metadata.get('routing_path', 'unknown')}")
                print(f"Agents Used: {metadata.get('agents_used', [])}")
                print(f"Response Preview: {response_text[:200]}...")
                
                # Analyze response format
                self._analyze_response_format(test_case["expected_type"], response_text, metadata)
                
            except Exception as e:
                print(f"❌ Error testing response type: {e}")
        
        return True
    
    def _analyze_response_format(self, expected_type: str, response_text: str, metadata: Dict):
        """Analyze the format and structure of responses"""
        analysis = {
            "has_synthesis_header": "Synthesis:" in response_text,
            "has_insight_component": "- Insight:" in response_text,
            "has_watch_component": "- Watch:" in response_text, 
            "has_direction_component": "- Direction:" in response_text,
            "ends_with_question": response_text.strip().endswith("?"),
            "has_bullet_points": "- " in response_text,
            "word_count": len(response_text.split()),
            "agents_used": metadata.get("agents_used", [])
        }
        
        print(f"Format Analysis: {analysis}")
        return analysis

    async def run_domain_expert_database_testing(self):
        """3. Domain Expert Database & Web Integration Testing"""
        print("\n🗄️ DOMAIN EXPERT DATABASE & WEB INTEGRATION TESTING")
        print("=" * 80)

        try:
            from agents.domain_expert.domain_expert import DomainExpertAgent

            domain_expert = DomainExpertAgent()

            # Test database search capabilities
            database_test_cases = [
                {
                    "query": "community center design principles",
                    "expected": "Should find relevant design principles in database",
                    "type": "general_knowledge"
                },
                {
                    "query": "examples of community centers in hot climates",
                    "expected": "Should find specific project examples",
                    "type": "example_projects"
                },
                {
                    "query": "passive cooling strategies",
                    "expected": "Should find technical strategies",
                    "type": "technical_knowledge"
                },
                {
                    "query": "very specific obscure architectural term",
                    "expected": "Should fallback to AI generation",
                    "type": "fallback_test"
                }
            ]

            for test_case in database_test_cases:
                print(f"\n🔍 Testing Database Query: {test_case['query']}")

                try:
                    # Test knowledge retrieval
                    result = await domain_expert.get_knowledge(test_case["query"])

                    print(f"Result Type: {result.get('source', 'unknown')}")
                    print(f"Content Length: {len(result.get('content', ''))}")
                    print(f"Has References: {'references' in result}")
                    print(f"Preview: {result.get('content', '')[:150]}...")

                    # Analyze search quality
                    self._analyze_database_search_quality(test_case, result)

                except Exception as e:
                    print(f"❌ Database test error: {e}")

            # Test web integration for example projects
            print(f"\n🌐 Testing Web Integration for Example Projects")
            try:
                web_result = await domain_expert.get_example_projects("sustainable community centers")
                print(f"Web Search Results: {len(web_result.get('projects', []))}")
                print(f"Has Links: {any('url' in p for p in web_result.get('projects', []))}")
            except Exception as e:
                print(f"❌ Web integration test error: {e}")

        except ImportError as e:
            print(f"❌ Could not import domain expert: {e}")

        return True

    def _analyze_database_search_quality(self, test_case: Dict, result: Dict):
        """Analyze the quality of database search results"""
        analysis = {
            "has_content": bool(result.get("content")),
            "content_length": len(result.get("content", "")),
            "has_references": "references" in result,
            "source_type": result.get("source", "unknown"),
            "relevance_score": self._calculate_relevance_score(test_case["query"], result.get("content", ""))
        }
        print(f"Search Quality: {analysis}")
        return analysis

    def _calculate_relevance_score(self, query: str, content: str) -> float:
        """Simple relevance scoring based on keyword overlap"""
        if not content:
            return 0.0

        query_words = set(query.lower().split())
        content_words = set(content.lower().split())
        overlap = len(query_words.intersection(content_words))
        return overlap / len(query_words) if query_words else 0.0

    async def run_gamification_system_verification(self):
        """4. Gamification System Verification"""
        print("\n🎮 GAMIFICATION SYSTEM VERIFICATION")
        print("=" * 80)

        # Test gamification triggers
        gamification_test_cases = [
            {
                "input": "I think this design will work perfectly for everyone",
                "expected_trigger": "overconfidence_challenge",
                "description": "Should trigger overconfidence challenge"
            },
            {
                "input": "Just tell me what to do",
                "expected_trigger": "cognitive_offloading_prevention",
                "description": "Should prevent cognitive offloading"
            },
            {
                "input": "I've been working on this for hours and I'm stuck",
                "expected_trigger": "encouragement_boost",
                "description": "Should provide encouragement"
            }
        ]

        for test_case in gamification_test_cases:
            print(f"\n🎯 Testing Gamification: {test_case['expected_trigger']}")
            print(f"Input: {test_case['input']}")

            try:
                # Test through full system to see gamification metadata
                from orchestration.orchestrator import ArchMentorOrchestrator
                from state_manager import ArchMentorState

                orchestrator = ArchMentorOrchestrator()
                state = ArchMentorState()
                state.messages = [{"role": "user", "content": test_case["input"]}]

                result = await orchestrator.process_student_input(state)
                metadata = result.get("response_metadata", {})

                # Check for gamification metadata
                gamification_data = metadata.get("gamification", {})
                print(f"Gamification Triggered: {bool(gamification_data)}")
                print(f"Gamification Type: {gamification_data.get('type', 'none')}")
                print(f"Gamification Message: {gamification_data.get('message', 'none')}")

                self.gamification_tests.append({
                    "input": test_case["input"],
                    "expected": test_case["expected_trigger"],
                    "actual": gamification_data,
                    "triggered": bool(gamification_data)
                })

            except Exception as e:
                print(f"❌ Gamification test error: {e}")

        return True

    async def run_end_to_end_system_testing(self):
        """5. End-to-End System Testing"""
        print("\n🔄 END-TO-END SYSTEM TESTING")
        print("=" * 80)

        # Test complete workflows
        workflow_test_cases = [
            {
                "name": "Knowledge Request Workflow",
                "inputs": [
                    "What are some examples of community centers?",
                    "Can you show me more examples in hot climates?",
                    "What design principles do these examples follow?"
                ],
                "expected_flow": "knowledge_only → knowledge_only → knowledge_only"
            },
            {
                "name": "Design Guidance Workflow",
                "inputs": [
                    "I need help organizing my community center",
                    "I don't understand spatial hierarchy",
                    "Can you give me specific suggestions for the entrance?"
                ],
                "expected_flow": "balanced_guidance → socratic_clarification → balanced_guidance"
            },
            {
                "name": "Mixed Interaction Workflow",
                "inputs": [
                    "What are passive cooling strategies?",
                    "How should I apply these to my project?",
                    "This approach seems perfect for my site"
                ],
                "expected_flow": "knowledge_only → balanced_guidance → cognitive_challenge"
            }
        ]

        for workflow in workflow_test_cases:
            print(f"\n🔄 Testing Workflow: {workflow['name']}")

            try:
                from orchestration.orchestrator import ArchMentorOrchestrator
                from state_manager import ArchMentorState

                orchestrator = ArchMentorOrchestrator()
                state = ArchMentorState()

                workflow_results = []

                for i, user_input in enumerate(workflow["inputs"]):
                    print(f"  Step {i+1}: {user_input}")

                    # Add message to conversation history
                    state.messages.append({"role": "user", "content": user_input})

                    # Process input
                    result = await orchestrator.process_student_input(state)

                    # Add response to conversation history
                    response = result.get("final_response", "")
                    state.messages.append({"role": "assistant", "content": response})

                    # Record result
                    metadata = result.get("response_metadata", {})
                    route = metadata.get("routing_path", "unknown")

                    workflow_results.append({
                        "step": i + 1,
                        "input": user_input,
                        "route": route,
                        "response_length": len(response),
                        "has_gamification": bool(metadata.get("gamification"))
                    })

                    print(f"    Route: {route}")
                    print(f"    Response Length: {len(response)}")

                # Analyze workflow
                actual_flow = " → ".join([r["route"] for r in workflow_results])
                print(f"  Expected Flow: {workflow['expected_flow']}")
                print(f"  Actual Flow: {actual_flow}")

                self.end_to_end_tests.append({
                    "workflow_name": workflow["name"],
                    "expected_flow": workflow["expected_flow"],
                    "actual_flow": actual_flow,
                    "results": workflow_results
                })

            except Exception as e:
                print(f"❌ Workflow test error: {e}")

        return True

    def generate_comprehensive_report(self):
        """Generate comprehensive analysis report"""
        print("\n📊 GENERATING COMPREHENSIVE REPORT")
        print("=" * 80)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"learning_tool_analysis_report_{timestamp}.json"

        # Compile all results
        report = {
            "analysis_timestamp": datetime.now().isoformat(),
            "routing_classification_analysis": {
                "route_analyses": {k: asdict(v) for k, v in self.route_analyses.items()},
                "overall_accuracy": self._calculate_overall_routing_accuracy()
            },
            "response_type_analysis": {
                "tested_response_types": list(self.test_cases.keys()),
                "format_compliance": "See individual test results"
            },
            "domain_expert_database_testing": {
                "database_tests": self.domain_expert_tests,
                "search_quality_summary": "See individual test results"
            },
            "gamification_system_verification": {
                "gamification_tests": self.gamification_tests,
                "trigger_success_rate": self._calculate_gamification_success_rate()
            },
            "end_to_end_system_testing": {
                "workflow_tests": self.end_to_end_tests,
                "workflow_success_rate": self._calculate_workflow_success_rate()
            },
            "recommendations": self._generate_recommendations()
        }

        # Save report
        with open(report_filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        print(f"📄 Report saved to: {report_filename}")

        # Print summary
        self._print_executive_summary(report)

        return report

    def _calculate_overall_routing_accuracy(self) -> float:
        """Calculate overall routing accuracy across all tests"""
        total_tests = 0
        successful_tests = 0

        for route_analysis in self.route_analyses.values():
            for result in route_analysis.test_results:
                total_tests += 1
                if result.success:
                    successful_tests += 1

        return (successful_tests / total_tests * 100) if total_tests > 0 else 0.0

    def _calculate_gamification_success_rate(self) -> float:
        """Calculate gamification trigger success rate"""
        if not self.gamification_tests:
            return 0.0

        triggered = sum(1 for test in self.gamification_tests if test["triggered"])
        return (triggered / len(self.gamification_tests) * 100)

    def _calculate_workflow_success_rate(self) -> float:
        """Calculate workflow success rate"""
        if not self.end_to_end_tests:
            return 0.0

        # Simple success metric: did the workflow complete without errors
        successful = len(self.end_to_end_tests)  # If it completed, it's successful
        return (successful / len(self.end_to_end_tests) * 100)

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []

        # Routing accuracy recommendations
        routing_accuracy = self._calculate_overall_routing_accuracy()
        if routing_accuracy < 90:
            recommendations.append("Improve routing classification accuracy - currently below 90%")

        # Gamification recommendations
        gamification_rate = self._calculate_gamification_success_rate()
        if gamification_rate < 50:
            recommendations.append("Enhance gamification trigger detection - low activation rate")

        # Add more specific recommendations based on test results
        recommendations.extend([
            "Consider implementing more sophisticated semantic search for domain expert database",
            "Add visual indicators for different response types in UI",
            "Implement conversation context awareness for better routing decisions",
            "Add user feedback mechanism to improve classification accuracy over time"
        ])

        return recommendations

    def _print_executive_summary(self, report: Dict):
        """Print executive summary of analysis results"""
        print("\n📋 EXECUTIVE SUMMARY")
        print("=" * 80)

        routing_accuracy = report["routing_classification_analysis"]["overall_accuracy"]
        gamification_rate = report["gamification_system_verification"]["trigger_success_rate"]
        workflow_rate = report["end_to_end_system_testing"]["workflow_success_rate"]

        print(f"🎯 Overall Routing Accuracy: {routing_accuracy:.1f}%")
        print(f"🎮 Gamification Trigger Rate: {gamification_rate:.1f}%")
        print(f"🔄 Workflow Completion Rate: {workflow_rate:.1f}%")

        print(f"\n📝 Key Recommendations:")
        for i, rec in enumerate(report["recommendations"][:5], 1):
            print(f"  {i}. {rec}")

        print(f"\n✅ Analysis completed successfully!")
        print(f"📊 Total test cases executed: {sum(len(ra.test_results) for ra in self.route_analyses.values())}")

if __name__ == "__main__":
    async def main():
        framework = ComprehensiveAnalysisFramework()

        print("🔍 COMPREHENSIVE LEARNING TOOL ANALYSIS")
        print("=" * 120)

        # Run all analyses
        await framework.run_routing_classification_analysis()
        await framework.run_response_type_analysis()
        await framework.run_domain_expert_database_testing()
        await framework.run_gamification_system_verification()
        await framework.run_end_to_end_system_testing()

        # Generate comprehensive report
        framework.generate_comprehensive_report()

        print("\n✅ Comprehensive Analysis Complete!")

    asyncio.run(main())
