"""
Comprehensive Test Script for Mentor.py Application Workflow

This script validates the entire mentor.py application including:
- Routing logic and decision trees
- Interaction types and response generation
- Gamification triggers and integration
- Building type extraction and persistence
- Context persistence across conversations
- Complete route coverage testing

Usage: python comprehensive_mentor_test.py
"""

import os
import sys
import asyncio
import time
import json
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import traceback

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Add thesis-agents to path
THESIS_AGENTS_DIR = os.path.join(PROJECT_ROOT, 'thesis-agents')
if THESIS_AGENTS_DIR not in sys.path:
    sys.path.insert(0, THESIS_AGENTS_DIR)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import required modules
try:
    from orchestration.langgraph_orchestrator import LangGraphOrchestrator
    from state_manager import ArchMentorState
    from utils.routing_decision_tree import AdvancedRoutingDecisionTree, RouteType
    from agents.context_agent import ContextAgent
    print("✅ Successfully imported all required modules")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

@dataclass
class TestResult:
    """Test result data structure"""
    test_name: str
    passed: bool
    route_taken: str
    response_type: str
    gamification_triggered: bool
    building_type_extracted: str
    response_time: float
    error_message: str = ""
    response_content: str = ""
    routing_reasoning: str = ""

@dataclass
class ConversationTest:
    """Multi-turn conversation test scenario"""
    name: str
    description: str
    messages: List[str]
    expected_routes: List[str]
    expected_building_type: str
    expected_gamification: List[bool]

class ComprehensiveMentorTester:
    """Comprehensive testing framework for the mentor application"""
    
    def __init__(self):
        self.orchestrator = None
        self.state_manager = None
        self.results: List[TestResult] = []
        self.conversation_results: Dict[str, List[TestResult]] = {}
        
    async def initialize(self):
        """Initialize the testing environment"""
        print("🚀 Initializing Comprehensive Mentor Test Suite...")
        
        try:
            # Initialize orchestrator
            self.orchestrator = LangGraphOrchestrator()
            print("✅ LangGraph Orchestrator initialized")
            
            # Initialize state manager
            self.state_manager = ArchMentorState()
            print("✅ State Manager initialized")
            
            # Verify API keys
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment")
            print("✅ API keys verified")
            
        except Exception as e:
            print(f"❌ Initialization failed: {e}")
            raise
    
    def get_test_scenarios(self) -> List[ConversationTest]:
        """Define comprehensive test scenarios"""
        return [
            ConversationTest(
                name="Progressive Opening → Design Guidance with Gamification",
                description="Test the complete flow from first message to gamified design guidance",
                messages=[
                    "I'm designing a community center in an old warehouse building",
                    "I'm thinking about how to create flexible spaces that can adapt to different community needs",
                    "What are some examples of successful adaptive reuse projects?"
                ],
                expected_routes=["progressive_opening", "socratic_exploration", "knowledge_only"],
                expected_building_type="community_center",
                expected_gamification=[False, True, False]
            ),
            
            ConversationTest(
                name="Knowledge Request → Project Examples",
                description="Test knowledge-only routing with project example requests",
                messages=[
                    "I'm working on a library design project",
                    "Can you give me examples of libraries with innovative circulation systems?",
                    "What about specific projects that handle noise zoning well?"
                ],
                expected_routes=["progressive_opening", "knowledge_only", "knowledge_only"],
                expected_building_type="library",
                expected_gamification=[False, False, False]
            ),
            
            ConversationTest(
                name="Confusion Expression → Clarification",
                description="Test confusion handling and clarification routing",
                messages=[
                    "I'm designing a school with outdoor learning spaces",
                    "I don't understand how to balance security with openness",
                    "Can you help me understand this better?"
                ],
                expected_routes=["progressive_opening", "socratic_clarification", "supportive_scaffolding"],
                expected_building_type="school",
                expected_gamification=[False, False, False]
            ),
            
            ConversationTest(
                name="Multi-Agent Comprehensive → Evaluation",
                description="Test complex evaluation requests requiring multiple agents",
                messages=[
                    "I'm working on a hospital design with healing gardens",
                    "What do you think of my approach to integrating nature into clinical spaces?",
                    "Can you give me feedback from different perspectives?"
                ],
                expected_routes=["progressive_opening", "multi_agent_comprehensive", "multi_agent_comprehensive"],
                expected_building_type="hospital",
                expected_gamification=[False, True, False]
            ),
            
            ConversationTest(
                name="Cognitive Challenge Triggers",
                description="Test scenarios that should trigger cognitive challenges",
                messages=[
                    "I'm designing an office building with flexible workspaces",
                    "That makes sense, what's next?",
                    "Ok, I understand"
                ],
                expected_routes=["progressive_opening", "cognitive_challenge", "cognitive_challenge"],
                expected_building_type="office_building",
                expected_gamification=[False, True, True]
            )
        ]

    async def test_single_interaction(self, user_input: str, expected_route: str = None,
                                    expected_gamification: bool = None) -> TestResult:
        """Test a single user interaction"""
        start_time = time.time()

        try:
            # Add user input to state messages
            self.state_manager.messages.append({
                "role": "user",
                "content": user_input
            })

            # Process the interaction
            result = await self.orchestrator.process_student_input(self.state_manager)

            response_time = time.time() - start_time

            # Extract routing information
            route_taken = result.get("routing_path", "unknown")
            routing_reasoning = result.get("metadata", {}).get("routing_reasoning", "")

            # Extract response information
            response_content = result.get("response", "")

            # Check for gamification
            gamification_triggered = "gamification" in response_content.lower() or \
                                   any(keyword in response_content.lower() for keyword in
                                       ["challenge", "perspective", "role-play", "constraint"])

            # Extract building type from state
            building_type = getattr(self.state_manager.conversation_context, 'building_type', 'unknown') if hasattr(self.state_manager, 'conversation_context') else 'unknown'

            # Determine response type
            response_type = self._classify_response_type(response_content, route_taken)

            # Check if test passed
            passed = True
            error_message = ""

            if expected_route and route_taken != expected_route:
                passed = False
                error_message += f"Expected route {expected_route}, got {route_taken}. "

            if expected_gamification is not None and gamification_triggered != expected_gamification:
                passed = False
                error_message += f"Expected gamification {expected_gamification}, got {gamification_triggered}. "

            return TestResult(
                test_name=f"Single interaction: {user_input[:50]}...",
                passed=passed,
                route_taken=route_taken,
                response_type=response_type,
                gamification_triggered=gamification_triggered,
                building_type_extracted=building_type,
                response_time=response_time,
                error_message=error_message,
                response_content=response_content[:200] + "..." if len(response_content) > 200 else response_content,
                routing_reasoning=routing_reasoning
            )

        except Exception as e:
            response_time = time.time() - start_time
            return TestResult(
                test_name=f"Single interaction: {user_input[:50]}...",
                passed=False,
                route_taken="error",
                response_type="error",
                gamification_triggered=False,
                building_type_extracted="unknown",
                response_time=response_time,
                error_message=str(e),
                response_content="",
                routing_reasoning=""
            )

    async def test_conversation_flow(self, conversation: ConversationTest) -> List[TestResult]:
        """Test a complete conversation flow"""
        print(f"\n🔄 Testing conversation: {conversation.name}")
        print(f"   Description: {conversation.description}")

        # Reset state for new conversation - this is correct for testing full conversations
        self.state_manager = ArchMentorState()
        results = []

        for i, message in enumerate(conversation.messages):
            print(f"   Message {i+1}: {message[:50]}...")

            expected_route = conversation.expected_routes[i] if i < len(conversation.expected_routes) else None
            expected_gamification = conversation.expected_gamification[i] if i < len(conversation.expected_gamification) else None

            result = await self.test_single_interaction(
                user_input=message,
                expected_route=expected_route,
                expected_gamification=expected_gamification
            )

            result.test_name = f"{conversation.name} - Message {i+1}"
            results.append(result)

            # Add assistant response to state (user message already added in test_single_interaction)
            self.state_manager.messages.append({
                "role": "assistant",
                "content": result.response_content
            })

            # Small delay between messages
            await asyncio.sleep(0.1)

        # Check building type persistence
        final_building_type = results[-1].building_type_extracted if results else "unknown"
        if final_building_type != conversation.expected_building_type:
            print(f"   ⚠️ Building type mismatch: expected {conversation.expected_building_type}, got {final_building_type}")

        return results

    def _classify_response_type(self, response_content: str, route_taken: str) -> str:
        """Classify the type of response based on content and route"""
        content_lower = response_content.lower()

        if "example" in content_lower and "project" in content_lower:
            return "project_examples"
        elif "example" in content_lower:
            return "general_examples"
        elif any(word in content_lower for word in ["challenge", "constraint", "perspective"]):
            return "gamified_response"
        elif "question" in content_lower or "?" in response_content:
            return "socratic_question"
        elif route_taken == "knowledge_only":
            return "knowledge_delivery"
        elif route_taken == "progressive_opening":
            return "opening_response"
        else:
            return "guidance_response"

    async def run_all_tests(self):
        """Run all test scenarios"""
        print("🧪 Starting Comprehensive Mentor Test Suite")
        print("=" * 60)

        # Test individual route coverage
        await self._test_route_coverage()

        # Test conversation flows
        scenarios = self.get_test_scenarios()
        for scenario in scenarios:
            results = await self.test_conversation_flow(scenario)
            self.conversation_results[scenario.name] = results
            self.results.extend(results)

        # Test edge cases
        await self._test_edge_cases()

        # Generate comprehensive report
        self._generate_test_report()

    async def _test_route_coverage(self):
        """Test coverage of all routing paths with proper conversation context"""
        print("\n🛤️ Testing Route Coverage")

        route_tests = [
            # Progressive opening - first message
            {
                "input": "I'm designing a museum with interactive exhibits",
                "expected_route": "progressive_opening",
                "setup_messages": []  # Empty for first message
            },
            # Knowledge only - after establishing context
            {
                "input": "What is sustainable design?",
                "expected_route": "knowledge_only",
                "setup_messages": [
                    {"role": "user", "content": "I'm working on a green building project"},
                    {"role": "assistant", "content": "Great! Let's explore sustainable design together."}
                ]
            },
            # Socratic exploration - after some context
            {
                "input": "I'm exploring how light affects mood in spaces",
                "expected_route": "socratic_exploration",
                "setup_messages": [
                    {"role": "user", "content": "I'm designing a wellness center"},
                    {"role": "assistant", "content": "Wellness centers are fascinating spaces for healing."}
                ]
            },
            # Cognitive challenge - passive response
            {
                "input": "That makes sense",
                "expected_route": "cognitive_challenge",
                "setup_messages": [
                    {"role": "user", "content": "I'm designing a library"},
                    {"role": "assistant", "content": "Libraries need quiet and active zones."},
                    {"role": "user", "content": "Tell me about circulation patterns"},
                    {"role": "assistant", "content": "Circulation is about how people move through space."}
                ]
            },
            # Multi-agent comprehensive - evaluation request
            {
                "input": "What do you think of my design approach?",
                "expected_route": "multi_agent_comprehensive",
                "setup_messages": [
                    {"role": "user", "content": "I'm designing a school"},
                    {"role": "assistant", "content": "Schools are complex learning environments."}
                ]
            },
            # Socratic clarification - confusion
            {
                "input": "I don't understand how this works",
                "expected_route": "socratic_clarification",
                "setup_messages": [
                    {"role": "user", "content": "I'm working on a hospital design"},
                    {"role": "assistant", "content": "Hospital design involves complex circulation patterns."}
                ]
            },
            # Supportive scaffolding - help request
            {
                "input": "I need help with this concept",
                "expected_route": "supportive_scaffolding",
                "setup_messages": [
                    {"role": "user", "content": "I'm designing an office building"},
                    {"role": "assistant", "content": "Office design has evolved significantly."}
                ]
            },
            # Foundational building - basic knowledge request
            {
                "input": "Can you explain the basics of structural systems?",
                "expected_route": "foundational_building",
                "setup_messages": [
                    {"role": "user", "content": "I'm new to architecture"},
                    {"role": "assistant", "content": "Welcome to the world of architecture!"}
                ]
            },
            # Knowledge with challenge - examples with engagement
            {
                "input": "Give me examples of innovative facades",
                "expected_route": "knowledge_with_challenge",
                "setup_messages": [
                    {"role": "user", "content": "I'm working on a high-rise design"},
                    {"role": "assistant", "content": "High-rise design is an exciting challenge."}
                ]
            },
            # Balanced guidance - general guidance request
            {
                "input": "How should I approach this design problem?",
                "expected_route": "balanced_guidance",
                "setup_messages": [
                    {"role": "user", "content": "I'm designing a mixed-use development"},
                    {"role": "assistant", "content": "Mixed-use projects require careful planning."}
                ]
            }
        ]

        for test_case in route_tests:
            # Create fresh state with proper conversation history
            self.state_manager = ArchMentorState()

            # Set up conversation context
            self.state_manager.messages = test_case["setup_messages"].copy()

            # Test the interaction
            result = await self.test_single_interaction(
                test_case["input"],
                test_case["expected_route"]
            )
            result.test_name = f"Route Coverage: {test_case['expected_route']}"
            self.results.append(result)

    async def _test_edge_cases(self):
        """Test edge cases and error handling"""
        print("\n⚠️ Testing Edge Cases")

        edge_cases = [
            "",  # Empty input
            "a",  # Single character
            "?" * 100,  # Very long input
            "🏗️🎨🌟",  # Only emojis
            "HELP HELP HELP",  # Repeated words
        ]

        for case in edge_cases:
            self.state_manager = ArchMentorState()
            result = await self.test_single_interaction(case)
            result.test_name = f"Edge Case: {case[:20]}..."
            self.results.append(result)

    def _generate_test_report(self):
        """Generate comprehensive test report"""
        print("\n📊 COMPREHENSIVE TEST REPORT")
        print("=" * 60)

        # Overall statistics
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.passed)
        failed_tests = total_tests - passed_tests

        print(f"📈 OVERALL RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests} ({passed_tests/total_tests*100:.1f}%)")
        print(f"   Failed: {failed_tests} ({failed_tests/total_tests*100:.1f}%)")

        # Route coverage analysis
        routes_tested = set(r.route_taken for r in self.results if r.route_taken != "error")
        expected_routes = {
            "progressive_opening", "knowledge_only", "socratic_exploration",
            "cognitive_challenge", "multi_agent_comprehensive", "socratic_clarification",
            "supportive_scaffolding", "foundational_building", "knowledge_with_challenge",
            "balanced_guidance"
        }

        print(f"\n🛤️ ROUTE COVERAGE:")
        print(f"   Routes Tested: {len(routes_tested)}")
        print(f"   Expected Routes: {len(expected_routes)}")
        print(f"   Coverage: {len(routes_tested)/len(expected_routes)*100:.1f}%")

        missing_routes = expected_routes - routes_tested
        if missing_routes:
            print(f"   Missing Routes: {', '.join(missing_routes)}")

        # Gamification analysis
        gamified_responses = sum(1 for r in self.results if r.gamification_triggered)
        print(f"\n🎮 GAMIFICATION ANALYSIS:")
        print(f"   Gamified Responses: {gamified_responses}")
        print(f"   Gamification Rate: {gamified_responses/total_tests*100:.1f}%")

        # Performance analysis
        avg_response_time = sum(r.response_time for r in self.results) / total_tests
        max_response_time = max(r.response_time for r in self.results)
        print(f"\n⚡ PERFORMANCE METRICS:")
        print(f"   Average Response Time: {avg_response_time:.2f}s")
        print(f"   Maximum Response Time: {max_response_time:.2f}s")

        # Failed tests details
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS DETAILS:")
            for result in self.results:
                if not result.passed:
                    print(f"   • {result.test_name}")
                    print(f"     Route: {result.route_taken}")
                    print(f"     Error: {result.error_message}")

        # Save detailed report to file
        self._save_detailed_report()

    def _save_detailed_report(self):
        """Save detailed test report to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"mentor_test_report_{timestamp}.json"

        report_data = {
            "timestamp": timestamp,
            "summary": {
                "total_tests": len(self.results),
                "passed_tests": sum(1 for r in self.results if r.passed),
                "failed_tests": sum(1 for r in self.results if not r.passed),
                "routes_tested": list(set(r.route_taken for r in self.results if r.route_taken != "error")),
                "gamification_rate": sum(1 for r in self.results if r.gamification_triggered) / len(self.results) * 100,
                "avg_response_time": sum(r.response_time for r in self.results) / len(self.results)
            },
            "test_results": [
                {
                    "test_name": r.test_name,
                    "passed": r.passed,
                    "route_taken": r.route_taken,
                    "response_type": r.response_type,
                    "gamification_triggered": r.gamification_triggered,
                    "building_type_extracted": r.building_type_extracted,
                    "response_time": r.response_time,
                    "error_message": r.error_message,
                    "routing_reasoning": r.routing_reasoning
                }
                for r in self.results
            ],
            "conversation_results": {
                name: [
                    {
                        "test_name": r.test_name,
                        "passed": r.passed,
                        "route_taken": r.route_taken,
                        "response_type": r.response_type,
                        "gamification_triggered": r.gamification_triggered,
                        "building_type_extracted": r.building_type_extracted,
                        "response_time": r.response_time
                    }
                    for r in results
                ]
                for name, results in self.conversation_results.items()
            }
        }

        with open(filename, 'w') as f:
            json.dump(report_data, f, indent=2)

        print(f"\n💾 Detailed report saved to: {filename}")

async def main():
    """Main test execution function"""
    tester = ComprehensiveMentorTester()

    try:
        await tester.initialize()
        await tester.run_all_tests()
        print("\n✅ Test suite completed successfully!")

    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        traceback.print_exc()
        return 1

    return 0

def cleanup_outdated_test_files():
    """Remove outdated test files as requested"""
    outdated_files = [
        "debug_routing_classification.py",
        "evidence_based_routing_analysis.py",
        "final_system_test.py",
        "focused_system_analysis.py",
        "quick_routing_test.py",
        "rag_conversation_tester.py",
        "quick_conversation_debugger.py",
        "comprehensive_system_test.py",
        "comprehensive_analysis_framework.py",
        "comprehensive_routing_test.py"
    ]

    print("\n🧹 Cleaning up outdated test files...")
    removed_count = 0

    for filename in outdated_files:
        filepath = os.path.join(PROJECT_ROOT, filename)
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                print(f"   ✅ Removed: {filename}")
                removed_count += 1
            except Exception as e:
                print(f"   ❌ Failed to remove {filename}: {e}")
        else:
            print(f"   ℹ️ Not found: {filename}")

    print(f"\n🗑️ Cleanup complete: {removed_count} files removed")

if __name__ == "__main__":
    # Run cleanup first
    cleanup_outdated_test_files()

    # Run the comprehensive test suite
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
