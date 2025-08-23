#!/usr/bin/env python3
"""
Test all fixes including gamification game types and knowledge routing
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

async def test_comprehensive_fixes():
    """Test all fixes including gamification game variety"""
    
    print("🧪 COMPREHENSIVE FINAL TEST - ALL FIXES")
    print("=" * 60)
    
    try:
        from orchestration.langgraph_orchestrator import LangGraphOrchestrator
        from state_manager import ArchMentorState
        
        orchestrator = LangGraphOrchestrator()
        print("✅ Orchestrator initialized")
        
        # Test cases for all problems including gamification variety
        test_cases = [
            {
                "problem": "PROBLEM 1: Low engagement triggers",
                "messages": [
                    {"role": "user", "content": "I'm working on a community center"},
                    {"role": "assistant", "content": "Great! Community centers are wonderful spaces."},
                    {"role": "user", "content": "That makes sense"}
                ],
                "expected_route": "cognitive_challenge",
                "expected_gamification": True,
                "expected_game_type": "any"
            },
            {
                "problem": "PROBLEM 3: Knowledge with challenge routing",
                "messages": [
                    {"role": "user", "content": "I'm working on a community center"},
                    {"role": "assistant", "content": "Great! Community centers are wonderful spaces."},
                    {"role": "user", "content": "What are the best practices for circulation design?"}
                ],
                "expected_route": "knowledge_with_challenge",
                "expected_gamification": False,
                "expected_game_type": "none"
            },
            {
                "problem": "PROBLEM 4a: Role-play gamification",
                "messages": [
                    {"role": "user", "content": "I'm working on a community center"},
                    {"role": "assistant", "content": "Great! Community centers are wonderful spaces."},
                    {"role": "user", "content": "How would a visitor feel entering this space?"}
                ],
                "expected_route": "cognitive_challenge",
                "expected_gamification": True,
                "expected_game_type": "role_play"
            },
            {
                "problem": "PROBLEM 4b: Constraint gamification",
                "messages": [
                    {"role": "user", "content": "I'm working on a community center"},
                    {"role": "assistant", "content": "Great! Community centers are wonderful spaces."},
                    {"role": "user", "content": "I'm completely stuck on this circulation problem"}
                ],
                "expected_route": "cognitive_challenge",
                "expected_gamification": True,
                "expected_game_type": "constraint"
            },
            {
                "problem": "PROBLEM 4c: Detective gamification",
                "messages": [
                    {"role": "user", "content": "I'm working on a community center"},
                    {"role": "assistant", "content": "Great! Community centers are wonderful spaces."},
                    {"role": "user", "content": "Users seem to avoid the main entrance area"}
                ],
                "expected_route": "cognitive_challenge",
                "expected_gamification": True,
                "expected_game_type": "detective"
            },
            {
                "problem": "PROBLEM 4d: Alternative/Perspective shift gamification",
                "messages": [
                    {"role": "user", "content": "I'm working on a community center"},
                    {"role": "assistant", "content": "Great! Community centers are wonderful spaces."},
                    {"role": "user", "content": "I wonder what would happen if I changed the entrance location"}
                ],
                "expected_route": "cognitive_challenge",
                "expected_gamification": True,
                "expected_game_type": "perspective_shift"
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
                
                # Check game type (simplified detection)
                game_type_detected = "unknown"
                if "Role Play" in response_content or "◉ Role Play" in response_content:
                    game_type_detected = "role_play"
                elif "Constraint" in response_content or "◉ Constraint" in response_content:
                    game_type_detected = "constraint"
                elif "Detective" in response_content or "◉ Detective" in response_content:
                    game_type_detected = "detective"
                elif "Perspective" in response_content or "◉ Perspective" in response_content:
                    game_type_detected = "perspective_shift"
                elif gamification_triggered:
                    game_type_detected = "some_game"
                else:
                    game_type_detected = "none"
                
                # Check if test passed
                route_correct = route_taken == test_case["expected_route"]
                gamification_correct = gamification_triggered == test_case["expected_gamification"]
                
                # Game type check
                expected_game = test_case["expected_game_type"]
                if expected_game == "any":
                    game_type_correct = gamification_triggered
                elif expected_game == "none":
                    game_type_correct = not gamification_triggered
                else:
                    game_type_correct = game_type_detected == expected_game
                
                passed = route_correct and gamification_correct and game_type_correct
                
                print(f"📝 Input: \"{test_case['messages'][-1]['content'][:50]}...\"")
                print(f"🛣️  Route: {route_taken} (expected: {test_case['expected_route']})")
                print(f"🎮 Gamification: {gamification_triggered} (expected: {test_case['expected_gamification']})")
                print(f"🎯 Game Type: {game_type_detected} (expected: {expected_game})")
                
                if passed:
                    print("✅ PASSED")
                else:
                    print("❌ FAILED")
                    if not route_correct:
                        print(f"   Route mismatch: got {route_taken}, expected {test_case['expected_route']}")
                    if not gamification_correct:
                        print(f"   Gamification mismatch: got {gamification_triggered}, expected {test_case['expected_gamification']}")
                    if not game_type_correct:
                        print(f"   Game type mismatch: got {game_type_detected}, expected {expected_game}")
                
                results.append({
                    "problem": test_case["problem"],
                    "passed": passed,
                    "route_taken": route_taken,
                    "gamification_triggered": gamification_triggered,
                    "game_type_detected": game_type_detected
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
        print(f"\n📊 COMPREHENSIVE FINAL RESULTS")
        print("=" * 50)
        
        passed_tests = sum(1 for r in results if r.get("passed", False))
        total_tests = len(results)
        
        print(f"Tests passed: {passed_tests}/{total_tests}")
        print(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Detailed results
        print(f"\n📋 DETAILED RESULTS:")
        for result in results:
            status = "✅" if result.get("passed", False) else "❌"
            print(f"{status} {result['problem']}")
            if not result.get("passed", False) and "error" not in result:
                print(f"   Route: {result.get('route_taken')}")
                print(f"   Gamification: {result.get('gamification_triggered')}")
                print(f"   Game Type: {result.get('game_type_detected')}")
        
        if passed_tests == total_tests:
            print("\n🎉 ALL PROBLEMS COMPLETELY FIXED!")
            print("🎊 PERFECT SUCCESS: All routing and gamification issues resolved!")
        elif passed_tests >= total_tests * 0.8:
            print("\n✅ MOST PROBLEMS FIXED - EXCELLENT PROGRESS")
        else:
            print("\n⚠️ SOME PROBLEMS STILL NEED WORK")
            
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_comprehensive_fixes())
