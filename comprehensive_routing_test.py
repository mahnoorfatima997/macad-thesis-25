#!/usr/bin/env python3
"""
Comprehensive test of all routing paths with real API calls.
Tests all 14 routes mentioned in gamified_routing.md
"""

import sys
import os
import asyncio
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Add thesis-agents to path
sys.path.insert(0, 'thesis-agents')

from orchestration.orchestrator import LangGraphOrchestrator
from state_manager import ArchMentorState
from utils.routing_decision_tree import AdvancedRoutingDecisionTree, RoutingContext

class ComprehensiveRoutingTest:
    """Test all routing paths with real API calls."""
    
    def __init__(self):
        self.orchestrator = LangGraphOrchestrator()
        self.router = AdvancedRoutingDecisionTree()
        self.test_results = {}
        
    async def run_all_tests(self):
        """Run comprehensive tests for all routes."""
        print("🧪 COMPREHENSIVE ROUTING TEST")
        print("=" * 80)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Test cases for all 14 routes from gamified_routing.md with proper conversation context
        test_cases = [
            # 1. TOPIC_TRANSITION
            {
                "route": "topic_transition",
                "conversation": [
                    {"role": "user", "content": "I'm designing a community center for a diverse neighborhood"},
                    {"role": "assistant", "content": "That's exciting! Let's start by thinking about the spatial organization..."},
                    {"role": "user", "content": "Let's talk about materials now instead of layout"}
                ],
                "expected_intent": "topic_transition",
                "description": "User wants to change topics"
            },

            # 2. CONFUSION_EXPRESSION
            {
                "route": "confusion_expression",
                "conversation": [
                    {"role": "user", "content": "I'm designing a community center"},
                    {"role": "assistant", "content": "Consider the spatial hierarchy in your design..."},
                    {"role": "user", "content": "I'm confused about what you mean by spatial hierarchy"}
                ],
                "expected_intent": "confusion_expression",
                "description": "User expresses confusion"
            },

            # 3. KNOWLEDGE_REQUEST
            {
                "route": "knowledge_request",
                "conversation": [
                    {"role": "user", "content": "I'm working on a sustainable community center design"},
                    {"role": "user", "content": "What are the key principles of sustainable design?"}
                ],
                "expected_intent": "knowledge_request",
                "description": "Direct knowledge request"
            },

            # 4. EXAMPLE_REQUEST
            {
                "route": "example_request",
                "conversation": [
                    {"role": "user", "content": "I need to create flexible spaces in my community center"},
                    {"role": "user", "content": "Can you show me examples of flexible community spaces?"}
                ],
                "expected_intent": "example_request",
                "description": "Request for specific examples"
            },

            # 5. SOCRATIC_EXPLORATION
            {
                "route": "socratic_exploration",
                "conversation": [
                    {"role": "user", "content": "I'm designing a community center for a diverse neighborhood"},
                    {"role": "user", "content": "I'm thinking about how to create spaces that feel welcoming to everyone"}
                ],
                "expected_intent": "design_exploration",
                "description": "Exploratory design thinking"
            },

            # 6. DESIGN_GUIDANCE
            {
                "route": "design_guidance",
                "conversation": [
                    {"role": "user", "content": "I'm working on a community center project"},
                    {"role": "user", "content": "I need help organizing the layout of my community center"}
                ],
                "expected_intent": "design_guidance",
                "description": "Request for design guidance"
            },

            # 7. BALANCED_GUIDANCE
            {
                "route": "balanced_guidance",
                "conversation": [
                    {"role": "user", "content": "I'm designing a community center with multiple functions"},
                    {"role": "user", "content": "How should I approach the circulation design for this project?"}
                ],
                "expected_intent": "design_exploration",
                "description": "Balanced guidance request"
            },

            # 8. KNOWLEDGE_WITH_CHALLENGE
            {
                "route": "knowledge_with_challenge",
                "conversation": [
                    {"role": "user", "content": "I'm designing a community center that needs to be accessible"},
                    {"role": "user", "content": "Tell me about accessibility requirements"}
                ],
                "expected_intent": "knowledge_request",
                "description": "Knowledge request that could benefit from challenge"
            },

            # 9. COGNITIVE_CHALLENGE
            {
                "route": "cognitive_challenge",
                "conversation": [
                    {"role": "user", "content": "I've been working on this community center design"},
                    {"role": "assistant", "content": "How do you think different user groups will experience the space?"},
                    {"role": "user", "content": "This design is perfect and will work for everyone"}
                ],
                "expected_intent": "overconfident_statement",
                "description": "Overconfident statement triggering challenge"
            },

            # 10. DESIGN_PROBLEM - Explicit problem statement
            {
                "route": "design_problem",
                "conversation": [
                    {"role": "user", "content": "I'm working on a community center on a tight urban site"},
                    {"role": "user", "content": "I'm stuck on how to fit all the required spaces in this small site"}
                ],
                "expected_intent": "design_problem",
                "description": "Explicit design problem"
            },

            # 11. TECHNICAL_QUESTION
            {
                "route": "technical_question",
                "conversation": [
                    {"role": "user", "content": "I'm working on the accessibility details for my community center"},
                    {"role": "user", "content": "What are the ADA requirements for door widths?"}
                ],
                "expected_intent": "technical_question",
                "description": "Technical specification question"
            },

            # 12. EVALUATION_REQUEST
            {
                "route": "evaluation_request",
                "conversation": [
                    {"role": "user", "content": "I've developed an approach for organizing the community center spaces"},
                    {"role": "user", "content": "What do you think about my design approach?"}
                ],
                "expected_intent": "evaluation_request",
                "description": "Request for design evaluation"
            },

            # 13. FEEDBACK_REQUEST
            {
                "route": "feedback_request",
                "conversation": [
                    {"role": "user", "content": "I've created a layout for the community center"},
                    {"role": "user", "content": "Can you give me feedback on this layout?"}
                ],
                "expected_intent": "feedback_request",
                "description": "Request for specific feedback"
            },

            # 14. IMPLEMENTATION_REQUEST
            {
                "route": "implementation_request",
                "conversation": [
                    {"role": "user", "content": "I've finalized my community center design"},
                    {"role": "user", "content": "How do I actually build this design?"}
                ],
                "expected_intent": "implementation_request",
                "description": "Implementation guidance request"
            }
        ]
        
        # Run tests
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{'='*60}")
            print(f"TEST {i}/14: {test_case['route'].upper()}")
            print(f"{'='*60}")
            
            await self._run_single_test(test_case)
            
        # Print summary
        self._print_test_summary()
        
    async def _run_single_test(self, test_case: dict):
        """Run a single routing test with full orchestrator."""
        route_name = test_case["route"]
        conversation = test_case["conversation"]
        expected_intent = test_case["expected_intent"]
        description = test_case["description"]

        # Get the last user message as the input to test
        user_input = conversation[-1]["content"]

        print(f"📝 Description: {description}")
        print(f"🎯 Input: '{user_input}'")
        print(f"🔮 Expected Intent: {expected_intent}")
        print(f"💬 Conversation Length: {len(conversation)} messages")
        print()

        try:
            # Test routing classification first
            classification = {'user_input': user_input}
            context = RoutingContext(
                classification=classification,
                context_analysis={},
                routing_suggestions={}
            )

            intent = self.router.classify_user_intent(user_input, context)
            print(f"🧠 Classified Intent: {intent}")

            # Test full orchestrator with conversation history
            state = ArchMentorState()
            state.messages = conversation.copy()  # Use full conversation history
            state.current_design_brief = "Designing a community center for a diverse neighborhood"

            print("🚀 Running full orchestrator...")
            result = await self.orchestrator.process_student_input(state)
            
            # Extract results
            response_text = result.get("response_text", "")
            metadata = result.get("response_metadata", {})
            routing_path = metadata.get("routing_path", "unknown")
            agents_used = metadata.get("agents_used", [])
            
            print(f"📍 Actual Route: {routing_path}")
            print(f"🤖 Agents Used: {', '.join(agents_used) if agents_used else 'None'}")
            print(f"📝 Response Length: {len(response_text)} characters")
            
            # Check for gamification
            gamification_info = metadata.get("gamification", {})
            if gamification_info:
                print(f"🎮 Gamification: {gamification_info.get('trigger_type', 'Unknown')}")
            
            # Store results
            self.test_results[route_name] = {
                "expected_intent": expected_intent,
                "actual_intent": intent,
                "expected_route": route_name,
                "actual_route": routing_path,
                "agents_used": agents_used,
                "response_length": len(response_text),
                "gamification": bool(gamification_info),
                "success": True,
                "error": None
            }
            
            print("✅ Test completed successfully")
            
        except Exception as e:
            print(f"❌ Test failed: {str(e)}")
            self.test_results[route_name] = {
                "success": False,
                "error": str(e)
            }
            
    def _print_test_summary(self):
        """Print comprehensive test summary."""
        print(f"\n{'='*80}")
        print("📊 COMPREHENSIVE TEST SUMMARY")
        print(f"{'='*80}")
        
        successful_tests = sum(1 for r in self.test_results.values() if r.get("success", False))
        total_tests = len(self.test_results)
        
        print(f"✅ Successful Tests: {successful_tests}/{total_tests}")
        print(f"❌ Failed Tests: {total_tests - successful_tests}/{total_tests}")
        print()
        
        # Detailed results
        for route_name, result in self.test_results.items():
            if result.get("success", False):
                intent_match = "✅" if result["expected_intent"] == result["actual_intent"] else "⚠️"
                print(f"{intent_match} {route_name.upper()}")
                print(f"   Intent: {result['expected_intent']} → {result['actual_intent']}")
                print(f"   Route: {result['actual_route']}")
                print(f"   Agents: {', '.join(result['agents_used'])}")
                print(f"   Response: {result['response_length']} chars")
                if result['gamification']:
                    print(f"   🎮 Gamified: Yes")
                print()
            else:
                print(f"❌ {route_name.upper()}: {result['error']}")
                print()

async def main():
    """Main test function."""
    # Check API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ Error: OPENAI_API_KEY not found in environment variables")
        print("Please check your .env file")
        return
    
    print(f"✅ API Key found: {api_key[:10]}...")
    print()
    
    # Run comprehensive test
    test_runner = ComprehensiveRoutingTest()
    await test_runner.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
