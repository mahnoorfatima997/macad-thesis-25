#!/usr/bin/env python3
"""
COMPREHENSIVE ROUTING & GAMIFICATION TEST
Tests all routes, gamification triggers, and response quality.
Enhanced version of comprehensive_mentor_test.py with gamification logic.
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

# Add project paths
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
THESIS_AGENTS_DIR = os.path.join(PROJECT_ROOT, 'thesis-agents')
sys.path.insert(0, PROJECT_ROOT)
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
    """Enhanced test result with gamification analysis"""
    test_name: str
    passed: bool
    route_taken: str
    expected_route: str
    response_type: str
    gamification_triggered: bool
    expected_gamification: bool
    building_type_extracted: str
    response_time: float
    response_quality_score: float
    gamification_type: str = ""
    error_message: str = ""
    response_content: str = ""
    routing_reasoning: str = ""
    context_understanding: float = 0.0

@dataclass
class RouteTestCase:
    """Test case for specific route"""
    name: str
    user_input: str
    expected_route: str
    expected_gamification: bool
    setup_messages: List[Dict[str, str]]
    context_keywords: List[str]
    description: str

class ComprehensiveRoutingGamificationTester:
    """Enhanced comprehensive testing framework"""
    
    def __init__(self):
        self.orchestrator = None
        self.state_manager = None
        self.results: List[TestResult] = []
        self.route_coverage = {}
        self.gamification_patterns = {}
        
    async def initialize(self):
        """Initialize the testing environment"""
        print("🚀 Initializing Comprehensive Routing & Gamification Test Suite...")
        
        try:
            self.orchestrator = LangGraphOrchestrator()
            print("✅ LangGraph Orchestrator initialized")
            
            # Verify API keys
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment")
            print("✅ API keys verified")
            
        except Exception as e:
            print(f"❌ Initialization failed: {e}")
            raise

    def get_comprehensive_route_tests(self) -> List[RouteTestCase]:
        """Define comprehensive test cases for all routes with gamification"""
        return [
            # 1. PROGRESSIVE_OPENING - First message
            RouteTestCase(
                name="Progressive Opening - First Message",
                user_input="I'm designing a community center in a converted warehouse",
                expected_route="progressive_opening",
                expected_gamification=False,
                setup_messages=[],
                context_keywords=["community center", "warehouse", "converted"],
                description="First message should trigger progressive opening without gamification"
            ),
            
            # 2. KNOWLEDGE_ONLY - Pure knowledge request
            RouteTestCase(
                name="Knowledge Only - Best Practices",
                user_input="What are the best practices for circulation design in community centers?",
                expected_route="knowledge_only",
                expected_gamification=False,
                setup_messages=[
                    {"role": "user", "content": "I'm working on a community center project"},
                    {"role": "assistant", "content": "Great! Community centers are fascinating spaces for bringing people together."}
                ],
                context_keywords=["best practices", "circulation", "community center"],
                description="Pure knowledge request should not trigger gamification"
            ),
            
            # 3. KNOWLEDGE_ONLY - Technical question
            RouteTestCase(
                name="Knowledge Only - Technical Question",
                user_input="What are ADA door width requirements for public buildings?",
                expected_route="knowledge_only",
                expected_gamification=False,
                setup_messages=[
                    {"role": "user", "content": "I'm designing a library"},
                    {"role": "assistant", "content": "Libraries are wonderful spaces for learning and community."}
                ],
                context_keywords=["ADA", "door width", "requirements"],
                description="Technical questions should go to knowledge_only without gamification"
            ),
            
            # 4. SOCRATIC_EXPLORATION - Design thinking
            RouteTestCase(
                name="Socratic Exploration - Design Thinking",
                user_input="I'm exploring how natural light affects learning in classroom spaces",
                expected_route="socratic_exploration",
                expected_gamification=True,
                setup_messages=[
                    {"role": "user", "content": "I'm designing a school"},
                    {"role": "assistant", "content": "School design is crucial for creating effective learning environments."}
                ],
                context_keywords=["natural light", "learning", "classroom"],
                description="Design exploration should trigger gamification"
            ),
            
            # 5. COGNITIVE_CHALLENGE - Passive response
            RouteTestCase(
                name="Cognitive Challenge - Passive Response",
                user_input="That makes sense",
                expected_route="cognitive_challenge",
                expected_gamification=True,
                setup_messages=[
                    {"role": "user", "content": "I'm designing a hospital"},
                    {"role": "assistant", "content": "Hospital design involves complex circulation and healing environments."},
                    {"role": "user", "content": "Tell me about wayfinding in hospitals"},
                    {"role": "assistant", "content": "Wayfinding is crucial for reducing stress and improving patient experience."}
                ],
                context_keywords=["makes sense"],
                description="Passive responses should trigger cognitive challenges"
            ),
            
            # 6. COGNITIVE_CHALLENGE - Overconfident
            RouteTestCase(
                name="Cognitive Challenge - Overconfident",
                user_input="I already know about sustainable design, what's next?",
                expected_route="cognitive_challenge", 
                expected_gamification=True,
                setup_messages=[
                    {"role": "user", "content": "I'm working on a green office building"},
                    {"role": "assistant", "content": "Sustainable office design is an exciting challenge."}
                ],
                context_keywords=["already know", "what's next"],
                description="Overconfident statements should trigger cognitive challenges"
            ),
            
            # 7. SOCRATIC_CLARIFICATION - Confusion
            RouteTestCase(
                name="Socratic Clarification - Confusion",
                user_input="I'm not sure how to balance privacy and openness in my design",
                expected_route="socratic_clarification",
                expected_gamification=True,
                setup_messages=[
                    {"role": "user", "content": "I'm designing a mixed-use residential building"},
                    {"role": "assistant", "content": "Mixed-use buildings require careful consideration of different user needs."}
                ],
                context_keywords=["not sure", "balance", "privacy", "openness"],
                description="Confusion expressions should trigger clarification with gamification"
            ),
            
            # 8. MULTI_AGENT_COMPREHENSIVE - Evaluation request
            RouteTestCase(
                name="Multi-Agent Comprehensive - Evaluation",
                user_input="What do you think of my approach to creating flexible learning spaces?",
                expected_route="multi_agent_comprehensive",
                expected_gamification=True,
                setup_messages=[
                    {"role": "user", "content": "I'm designing an innovative school"},
                    {"role": "assistant", "content": "Innovative school design can transform education."}
                ],
                context_keywords=["what do you think", "approach", "flexible learning"],
                description="Evaluation requests should trigger multi-agent with gamification"
            ),
            
            # 9. KNOWLEDGE_WITH_CHALLENGE - High understanding
            RouteTestCase(
                name="Knowledge with Challenge - Advanced Question",
                user_input="How do biophilic design principles apply to healthcare environments?",
                expected_route="knowledge_with_challenge",
                expected_gamification=True,
                setup_messages=[
                    {"role": "user", "content": "I'm designing a rehabilitation center"},
                    {"role": "assistant", "content": "Rehabilitation centers benefit greatly from healing-focused design."}
                ],
                context_keywords=["biophilic design", "healthcare", "principles"],
                description="Advanced questions should trigger knowledge with challenge"
            ),
            
            # 10. SUPPORTIVE_SCAFFOLDING - Help request
            RouteTestCase(
                name="Supportive Scaffolding - Help Request",
                user_input="I need help understanding how to approach this design problem",
                expected_route="supportive_scaffolding",
                expected_gamification=False,
                setup_messages=[
                    {"role": "user", "content": "I'm new to architecture"},
                    {"role": "assistant", "content": "Welcome to architecture! It's a wonderful field."}
                ],
                context_keywords=["need help", "understanding", "design problem"],
                description="Help requests should trigger supportive scaffolding"
            )
        ]

    async def test_single_route(self, test_case: RouteTestCase) -> TestResult:
        """Test a single route with comprehensive analysis"""
        start_time = time.time()

        try:
            # Create fresh state with setup messages
            self.state_manager = ArchMentorState()
            self.state_manager.messages = test_case.setup_messages.copy()

            # Add user input
            self.state_manager.messages.append({
                "role": "user",
                "content": test_case.user_input
            })

            # Process the interaction
            result = await self.orchestrator.process_student_input(self.state_manager)
            response_time = time.time() - start_time

            # Extract routing information
            route_taken = result.get("routing_path", "unknown")
            routing_reasoning = result.get("metadata", {}).get("routing_reasoning", "")
            response_content = result.get("response", "")

            # Analyze gamification
            gamification_analysis = self._analyze_gamification(response_content)

            # Analyze response quality
            quality_score = self._analyze_response_quality(
                response_content, test_case.context_keywords, route_taken
            )

            # Analyze context understanding
            context_score = self._analyze_context_understanding(
                response_content, test_case.context_keywords
            )

            # Extract building type
            building_type = self._extract_building_type(self.state_manager)

            # Determine if test passed
            route_correct = route_taken == test_case.expected_route
            gamification_correct = gamification_analysis["triggered"] == test_case.expected_gamification

            passed = route_correct and gamification_correct
            error_message = ""

            if not route_correct:
                error_message += f"Route mismatch: expected {test_case.expected_route}, got {route_taken}. "
            if not gamification_correct:
                error_message += f"Gamification mismatch: expected {test_case.expected_gamification}, got {gamification_analysis['triggered']}. "

            return TestResult(
                test_name=test_case.name,
                passed=passed,
                route_taken=route_taken,
                expected_route=test_case.expected_route,
                response_type=self._classify_response_type(response_content, route_taken),
                gamification_triggered=gamification_analysis["triggered"],
                expected_gamification=test_case.expected_gamification,
                building_type_extracted=building_type,
                response_time=response_time,
                response_quality_score=quality_score,
                gamification_type=gamification_analysis["type"],
                error_message=error_message,
                response_content=response_content[:300] + "..." if len(response_content) > 300 else response_content,
                routing_reasoning=routing_reasoning,
                context_understanding=context_score
            )

        except Exception as e:
            response_time = time.time() - start_time
            return TestResult(
                test_name=test_case.name,
                passed=False,
                route_taken="error",
                expected_route=test_case.expected_route,
                response_type="error",
                gamification_triggered=False,
                expected_gamification=test_case.expected_gamification,
                building_type_extracted="unknown",
                response_time=response_time,
                response_quality_score=0.0,
                error_message=str(e),
                response_content="",
                routing_reasoning="",
                context_understanding=0.0
            )

    def _analyze_gamification(self, response_content: str) -> Dict[str, Any]:
        """Analyze gamification elements in response"""
        content_lower = response_content.lower()

        # Gamification indicators
        challenge_indicators = ["challenge", "constraint", "twist", "curveball", "reality check"]
        perspective_indicators = ["perspective", "role-play", "imagine", "lens", "viewpoint"]
        interactive_indicators = ["choose", "select", "option", "a)", "b)", "c)", "🎯", "🎮"]
        game_indicators = ["game", "detective", "experiment", "lab", "bridge"]

        triggered = False
        gamification_type = "none"

        if any(indicator in content_lower for indicator in challenge_indicators):
            triggered = True
            gamification_type = "challenge"
        elif any(indicator in content_lower for indicator in perspective_indicators):
            triggered = True
            gamification_type = "perspective"
        elif any(indicator in content_lower for indicator in interactive_indicators):
            triggered = True
            gamification_type = "interactive"
        elif any(indicator in content_lower for indicator in game_indicators):
            triggered = True
            gamification_type = "game"

        return {
            "triggered": triggered,
            "type": gamification_type,
            "indicators_found": [
                ind for ind in challenge_indicators + perspective_indicators +
                interactive_indicators + game_indicators
                if ind in content_lower
            ]
        }

    def _analyze_response_quality(self, response_content: str, context_keywords: List[str], route_taken: str) -> float:
        """Analyze response quality (0.0 to 1.0)"""
        if not response_content:
            return 0.0

        score = 0.0

        # Length appropriateness (0.2 points)
        if 50 <= len(response_content) <= 1000:
            score += 0.2
        elif len(response_content) > 1000:
            score += 0.1

        # Context keyword usage (0.3 points)
        keywords_found = sum(1 for keyword in context_keywords if keyword.lower() in response_content.lower())
        if keywords_found > 0:
            score += min(0.3, keywords_found / len(context_keywords) * 0.3)

        # Route-appropriate content (0.3 points)
        route_indicators = {
            "knowledge_only": ["principles", "practices", "requirements", "standards"],
            "socratic_exploration": ["explore", "consider", "think about", "what if"],
            "cognitive_challenge": ["challenge", "constraint", "twist", "perspective"],
            "socratic_clarification": ["clarify", "understand", "break down", "step by step"],
            "multi_agent_comprehensive": ["perspective", "evaluation", "analysis", "feedback"]
        }

        if route_taken in route_indicators:
            indicators = route_indicators[route_taken]
            indicators_found = sum(1 for ind in indicators if ind in response_content.lower())
            if indicators_found > 0:
                score += min(0.3, indicators_found / len(indicators) * 0.3)

        # Engagement elements (0.2 points)
        engagement_indicators = ["?", "!", "imagine", "consider", "think", "explore"]
        engagement_found = sum(1 for ind in engagement_indicators if ind in response_content.lower())
        if engagement_found > 0:
            score += min(0.2, engagement_found / len(engagement_indicators) * 0.2)

        return min(1.0, score)

    def _analyze_context_understanding(self, response_content: str, context_keywords: List[str]) -> float:
        """Analyze how well the response understands context (0.0 to 1.0)"""
        if not response_content or not context_keywords:
            return 0.0

        content_lower = response_content.lower()
        keywords_found = sum(1 for keyword in context_keywords if keyword.lower() in content_lower)

        return min(1.0, keywords_found / len(context_keywords))

    def _extract_building_type(self, state_manager: ArchMentorState) -> str:
        """Extract building type from state"""
        try:
            if hasattr(state_manager, 'conversation_context') and hasattr(state_manager.conversation_context, 'building_type'):
                return state_manager.conversation_context.building_type

            # Fallback: extract from messages
            for message in state_manager.messages:
                if message.get("role") == "user":
                    content = message.get("content", "").lower()
                    building_types = [
                        "community center", "library", "school", "hospital", "office",
                        "museum", "warehouse", "residential", "mixed-use"
                    ]
                    for building_type in building_types:
                        if building_type in content:
                            return building_type.replace(" ", "_")

            return "unknown"
        except:
            return "unknown"

    def _classify_response_type(self, response_content: str, route_taken: str) -> str:
        """Classify the type of response"""
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

    async def run_comprehensive_tests(self):
        """Run all comprehensive tests"""
        print("🧪 COMPREHENSIVE ROUTING & GAMIFICATION TEST SUITE")
        print("=" * 70)

        # Get all test cases
        test_cases = self.get_comprehensive_route_tests()

        print(f"🎯 Testing {len(test_cases)} comprehensive scenarios...")

        # Run all tests
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n--- TEST {i}: {test_case.name} ---")
            print(f"📝 Input: {test_case.user_input}")
            print(f"🎯 Expected Route: {test_case.expected_route}")
            print(f"🎮 Expected Gamification: {test_case.expected_gamification}")

            result = await self.test_single_route(test_case)
            self.results.append(result)

            # Display results
            if result.passed:
                print("✅ PASSED")
            else:
                print("❌ FAILED")
                print(f"   Error: {result.error_message}")

            print(f"🛣️  Route: {result.route_taken}")
            print(f"🎮 Gamification: {result.gamification_triggered} ({result.gamification_type})")
            print(f"📊 Quality Score: {result.response_quality_score:.2f}")
            print(f"🧠 Context Understanding: {result.context_understanding:.2f}")
            print(f"⚡ Response Time: {result.response_time:.2f}s")

            # Small delay between tests
            await asyncio.sleep(0.5)

        # Generate comprehensive report
        self._generate_comprehensive_report()

    def _generate_comprehensive_report(self):
        """Generate comprehensive test report"""
        print("\n📊 COMPREHENSIVE TEST REPORT")
        print("=" * 70)

        # Overall statistics
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.passed)
        failed_tests = total_tests - passed_tests

        print(f"📈 OVERALL RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests} ({passed_tests/total_tests*100:.1f}%)")
        print(f"   Failed: {failed_tests} ({failed_tests/total_tests*100:.1f}%)")

        # Route accuracy analysis
        route_correct = sum(1 for r in self.results if r.route_taken == r.expected_route)
        print(f"\n🛤️ ROUTING ACCURACY:")
        print(f"   Correct Routes: {route_correct}/{total_tests} ({route_correct/total_tests*100:.1f}%)")

        # Gamification analysis
        gamification_correct = sum(1 for r in self.results if r.gamification_triggered == r.expected_gamification)
        gamification_triggered = sum(1 for r in self.results if r.gamification_triggered)

        print(f"\n🎮 GAMIFICATION ANALYSIS:")
        print(f"   Correct Gamification: {gamification_correct}/{total_tests} ({gamification_correct/total_tests*100:.1f}%)")
        print(f"   Total Gamified: {gamification_triggered}/{total_tests} ({gamification_triggered/total_tests*100:.1f}%)")

        # Gamification types
        gamification_types = {}
        for result in self.results:
            if result.gamification_triggered:
                gamification_types[result.gamification_type] = gamification_types.get(result.gamification_type, 0) + 1

        if gamification_types:
            print(f"   Gamification Types: {dict(gamification_types)}")

        # Response quality analysis
        avg_quality = sum(r.response_quality_score for r in self.results) / total_tests
        avg_context = sum(r.context_understanding for r in self.results) / total_tests

        print(f"\n📊 RESPONSE QUALITY:")
        print(f"   Average Quality Score: {avg_quality:.2f}/1.0")
        print(f"   Average Context Understanding: {avg_context:.2f}/1.0")

        # Performance analysis
        avg_response_time = sum(r.response_time for r in self.results) / total_tests
        max_response_time = max(r.response_time for r in self.results)

        print(f"\n⚡ PERFORMANCE METRICS:")
        print(f"   Average Response Time: {avg_response_time:.2f}s")
        print(f"   Maximum Response Time: {max_response_time:.2f}s")

        # Route coverage
        routes_tested = set(r.route_taken for r in self.results if r.route_taken != "error")
        expected_routes = set(r.expected_route for r in self.results)

        print(f"\n🛤️ ROUTE COVERAGE:")
        print(f"   Routes Tested: {len(routes_tested)}")
        print(f"   Expected Routes: {len(expected_routes)}")
        print(f"   Coverage: {len(routes_tested)/len(expected_routes)*100:.1f}%")

        # Failed tests details
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS DETAILS:")
            for result in self.results:
                if not result.passed:
                    print(f"   • {result.test_name}")
                    print(f"     Route: {result.route_taken} (expected: {result.expected_route})")
                    print(f"     Gamification: {result.gamification_triggered} (expected: {result.expected_gamification})")
                    print(f"     Error: {result.error_message}")

        # Save detailed report
        self._save_detailed_report()

    def _save_detailed_report(self):
        """Save detailed test report to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"comprehensive_routing_gamification_report_{timestamp}.json"

        report_data = {
            "timestamp": timestamp,
            "summary": {
                "total_tests": len(self.results),
                "passed_tests": sum(1 for r in self.results if r.passed),
                "failed_tests": sum(1 for r in self.results if not r.passed),
                "route_accuracy": sum(1 for r in self.results if r.route_taken == r.expected_route) / len(self.results) * 100,
                "gamification_accuracy": sum(1 for r in self.results if r.gamification_triggered == r.expected_gamification) / len(self.results) * 100,
                "avg_quality_score": sum(r.response_quality_score for r in self.results) / len(self.results),
                "avg_context_understanding": sum(r.context_understanding for r in self.results) / len(self.results),
                "avg_response_time": sum(r.response_time for r in self.results) / len(self.results)
            },
            "test_results": [
                {
                    "test_name": r.test_name,
                    "passed": r.passed,
                    "route_taken": r.route_taken,
                    "expected_route": r.expected_route,
                    "gamification_triggered": r.gamification_triggered,
                    "expected_gamification": r.expected_gamification,
                    "gamification_type": r.gamification_type,
                    "response_quality_score": r.response_quality_score,
                    "context_understanding": r.context_understanding,
                    "response_time": r.response_time,
                    "error_message": r.error_message
                }
                for r in self.results
            ]
        }

        with open(filename, 'w') as f:
            json.dump(report_data, f, indent=2)

        print(f"\n💾 Detailed report saved to: {filename}")

async def main():
    """Main test execution function"""
    tester = ComprehensiveRoutingGamificationTester()

    try:
        await tester.initialize()
        await tester.run_comprehensive_tests()
        print("\n✅ Comprehensive test suite completed successfully!")

    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        traceback.print_exc()
        return 1

    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
