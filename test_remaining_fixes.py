#!/usr/bin/env python3
"""
Test the remaining two problem fixes
"""

import os
import sys
import asyncio

# Add project paths
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
THESIS_AGENTS_DIR = os.path.join(PROJECT_ROOT, 'thesis-agents')
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, THESIS_AGENTS_DIR)

from dotenv import load_dotenv
load_dotenv()

async def test_remaining_fixes():
    """Test the remaining two problem fixes"""
    
    print("🧪 TESTING REMAINING PROBLEM FIXES")
    print("=" * 50)
    
    try:
        from orchestration.langgraph_orchestrator import LangGraphOrchestrator
        from state_manager import ArchMentorState
        
        orchestrator = LangGraphOrchestrator()
        print("✅ Orchestrator initialized")
        
        # Test the two remaining problems
        test_cases = [
            {
                "problem": "PROBLEM 3: Knowledge with challenge should be used",
                "messages": [
                    {"role": "user", "content": "I'm working on a community center"},
                    {"role": "assistant", "content": "Great! Community centers are wonderful spaces."},
                    {"role": "user", "content": "What are the best practices for circulation design?"}
                ],
                "expected_route": "knowledge_with_challenge",
                "expected_gamification": False
            },
            {
                "problem": "PROBLEM 3b: Help requests should use supportive scaffolding",
                "messages": [
                    {"role": "user", "content": "I need help understanding how to approach this design problem"}
                ],
                "expected_route": "supportive_scaffolding",
                "expected_gamification": False
            }
        ]
        
        results = []
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n--- TEST {i}: {test_case['problem']} ---")
            
            try:
                # Create fresh state
                state = ArchMentorState()
                state.messages = test_case['messages'].copy()
                
                # Process the interaction
                result = await orchestrator.process_student_input(state)
                
                # Extract results
                route_taken = result.get("routing_path", "unknown")
                response_content = result.get("response", "")
                
                # Check gamification
                gamification_triggered = "🎮" in response_content or "challenge" in response_content.lower()
                
                # Check if test passed
                route_correct = route_taken == test_case["expected_route"]
                gamification_correct = gamification_triggered == test_case["expected_gamification"]
                
                passed = route_correct and gamification_correct
                
                print(f"📝 Input: \"{test_case['messages'][-1]['content']}\"")
                print(f"🛣️  Route: {route_taken} (expected: {test_case['expected_route']})")
                print(f"🎮 Gamification: {gamification_triggered} (expected: {test_case['expected_gamification']})")
                
                if passed:
                    print("✅ PASSED")
                else:
                    print("❌ FAILED")
                    if not route_correct:
                        print(f"   Route mismatch: got {route_taken}, expected {test_case['expected_route']}")
                    if not gamification_correct:
                        print(f"   Gamification mismatch: got {gamification_triggered}, expected {test_case['expected_gamification']}")
                
                results.append({
                    "problem": test_case["problem"],
                    "passed": passed,
                    "route_taken": route_taken,
                    "expected_route": test_case["expected_route"]
                })
                
            except Exception as e:
                print(f"❌ ERROR: {e}")
                results.append({
                    "problem": test_case["problem"],
                    "passed": False,
                    "error": str(e)
                })
            
            # Small delay between tests
            await asyncio.sleep(0.5)
        
        # Summary
        print(f"\n📊 REMAINING FIXES RESULTS")
        print("=" * 40)
        
        passed_tests = sum(1 for r in results if r.get("passed", False))
        total_tests = len(results)
        
        print(f"Tests passed: {passed_tests}/{total_tests}")
        
        if passed_tests == total_tests:
            print("🎉 ALL REMAINING PROBLEMS FIXED!")
            print("🎊 TOTAL SUCCESS: All 6 problems now resolved!")
        else:
            print("⚠️ Some problems still need work")
            for result in results:
                if not result.get("passed", False):
                    print(f"❌ {result['problem']}")
                    if "error" not in result:
                        print(f"   Route: {result.get('route_taken')} → {result.get('expected_route')}")
            
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_remaining_fixes())
