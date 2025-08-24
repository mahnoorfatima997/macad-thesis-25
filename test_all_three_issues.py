#!/usr/bin/env python3
"""
Test all three issues that were reported:
1. Transformation challenge triggering repeatedly on example requests
2. Database search not triggering web search for project examples
3. Too many debug prints slowing the app
"""

import sys
import os
import time
sys.path.append('.')
sys.path.append('thesis-agents')

from dotenv import load_dotenv
load_dotenv()

async def test_issue_1_transformation_repeat():
    """Test Issue 1: Transformation challenge not triggering on example requests"""
    print("🧪 TESTING ISSUE 1: Transformation challenge repeat prevention")
    print("=" * 60)
    
    try:
        from agents.cognitive_enhancement.processors.challenge_generator import ChallengeGeneratorProcessor
        from state_manager import ArchMentorState
        
        processor = ChallengeGeneratorProcessor()
        
        # Simulate conversation where user asks for examples after transformation discussion
        state = ArchMentorState()
        state.messages = [
            {'role': 'user', 'content': 'I am converting a warehouse to a community center'},
            {'role': 'assistant', 'content': 'Great transformation project! Tell me more.'},
            {'role': 'user', 'content': 'The site has some challenges'},
            {'role': 'user', 'content': 'can you give example projects for community center that has courtyards?'}
        ]
        
        # Test if gamification should be applied (should be FALSE for example requests)
        should_trigger = processor._should_apply_gamification(state, 'test_challenge', 'transformation')
        
        print(f"Conversation context: User discussed warehouse conversion, then asked for examples")
        print(f"Latest message: 'can you give example projects for community center that has courtyards?'")
        print(f"Should trigger gamification: {should_trigger}")
        print(f"Expected: False (should NOT trigger transformation again)")
        
        if not should_trigger:
            print("✅ ISSUE 1 FIXED: Example requests don't trigger repeated transformation challenges")
            return True
        else:
            print("❌ ISSUE 1 NOT FIXED: Example requests still trigger transformation challenges")
            return False
            
    except Exception as e:
        print(f"❌ Issue 1 test failed: {e}")
        return False

async def test_issue_2_web_search():
    """Test Issue 2: Database search triggering web search when needed"""
    print("\n🧪 TESTING ISSUE 2: Database → Web search trigger")
    print("=" * 60)
    
    try:
        from agents.domain_expert.adapter import DomainExpertAgent
        from state_manager import ArchMentorState
        
        # Create test state with meaningful project context
        state = ArchMentorState()
        state.current_design_brief = "community_center"
        state.messages = [
            {"role": "user", "content": "I'm designing a community center"},
            {"role": "assistant", "content": "Great! Tell me more."},
            {"role": "user", "content": "I'm converting a warehouse"},
            {"role": "user", "content": "can you give example projects for community center that has courtyards?"}
        ]
        
        # Create domain expert
        domain_expert = DomainExpertAgent()
        
        print("User request: 'can you give example projects for community center that has courtyards?'")
        print("Context: User has discussed warehouse conversion (meaningful project context)")
        print("Expected: Should bypass cognitive protection and trigger web search if database lacks project names")
        
        # Test the knowledge provision
        context_classification = {
            "user_intent": "knowledge_seeking",
            "user_input": "can you give example projects for community center that has courtyards?",
            "is_project_example_request": True
        }
        
        analysis_result = {
            "gap_type": "example_gap",
            "project_context": "community_center"
        }
        
        routing_decision = {
            "route": "knowledge_only",
            "reason": "User requesting project examples"
        }
        
        start_time = time.time()
        result = await domain_expert.provide_knowledge(
            state=state,
            context_classification=context_classification,
            analysis_result=analysis_result,
            routing_decision=routing_decision
        )
        end_time = time.time()
        
        # Check results
        has_web_sources = any('http' in str(source) for source in result.sources_used)
        contains_sorry = "I'm sorry" in result.response_text
        is_cognitive_protection = "cognitive protection" in result.response_text.lower()
        response_length = len(result.response_text)
        
        print(f"Response time: {end_time - start_time:.2f} seconds")
        print(f"Response length: {response_length} characters")
        print(f"Has web sources: {has_web_sources}")
        print(f"Contains 'I'm sorry': {contains_sorry}")
        print(f"Is cognitive protection: {is_cognitive_protection}")
        
        if has_web_sources and not contains_sorry and not is_cognitive_protection:
            print("✅ ISSUE 2 FIXED: Web search triggered and provided specific project examples")
            return True
        elif is_cognitive_protection:
            print("⚠️ ISSUE 2 PARTIAL: Still triggering cognitive protection (may need further adjustment)")
            return False
        else:
            print("❌ ISSUE 2 NOT FIXED: Web search not triggered or still generic response")
            return False
            
    except Exception as e:
        print(f"❌ Issue 2 test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_issue_3_debug_prints():
    """Test Issue 3: Reduced debug prints for better performance"""
    print("\n🧪 TESTING ISSUE 3: Debug print reduction")
    print("=" * 60)
    
    try:
        # Check if debug prints have been commented out in key files
        files_to_check = [
            ('thesis-agents/agents/domain_expert/adapter.py', [
                '# print(f"🔍 DEBUG: Synthesizing',
                '# print(f"   📄 Result',
                '# print(f"🔍 DEBUG: Combined knowledge',
                '# ISSUE 3 FIX: Commented out verbose debug prints'
            ]),
            ('thesis-agents/agents/cognitive_enhancement/processors/challenge_generator.py', [
                '# ISSUE 3 FIX: Commented out verbose frequency debug prints',
                '# print(f"🎮 GAMIFICATION SKIP: Normal design statement',
                '# print(f"🎮 GAMIFICATION TRIGGER: Low engagement detected'
            ])
        ]
        
        debug_prints_commented = 0
        total_checks = 0
        
        for file_path, patterns in files_to_check:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                for pattern in patterns:
                    total_checks += 1
                    if pattern in content:
                        debug_prints_commented += 1
                        print(f"✅ Found commented debug print: {pattern[:50]}...")
                    else:
                        print(f"❌ Debug print not commented: {pattern[:50]}...")
                        
            except Exception as e:
                print(f"⚠️ Could not check {file_path}: {e}")
        
        print(f"\nDebug prints commented out: {debug_prints_commented}/{total_checks}")
        
        if debug_prints_commented >= total_checks * 0.8:  # At least 80% commented out
            print("✅ ISSUE 3 FIXED: Most debug prints have been commented out for better performance")
            return True
        else:
            print("⚠️ ISSUE 3 PARTIAL: Some debug prints still need to be commented out")
            return False
            
    except Exception as e:
        print(f"❌ Issue 3 test failed: {e}")
        return False

async def main():
    """Run all three issue tests"""
    print("🚀 COMPREHENSIVE ISSUE TESTING")
    print("Testing all three reported issues:")
    print("1. Transformation challenge triggering repeatedly")
    print("2. Database search not triggering web search")
    print("3. Too many debug prints slowing the app")
    print("=" * 80)
    
    # Run all tests
    issue1_fixed = await test_issue_1_transformation_repeat()
    issue2_fixed = await test_issue_2_web_search()
    issue3_fixed = test_issue_3_debug_prints()
    
    # Final summary
    print("\n" + "=" * 80)
    print("📊 FINAL ISSUE RESOLUTION REPORT")
    print("=" * 80)
    
    issues = [
        ("🔄 Issue 1: Transformation Repeat Prevention", issue1_fixed),
        ("🌐 Issue 2: Database → Web Search Trigger", issue2_fixed),
        ("⚡ Issue 3: Debug Print Reduction", issue3_fixed)
    ]
    
    all_fixed = True
    for issue_name, fixed in issues:
        status = "✅ FIXED" if fixed else "❌ NOT FIXED"
        print(f"{issue_name}: {status}")
        if not fixed:
            all_fixed = False
    
    print("\n" + "=" * 80)
    if all_fixed:
        print("🎉 ALL ISSUES RESOLVED! The application should now:")
        print("✅ Not trigger transformation challenges on example requests")
        print("✅ Properly trigger web search when database lacks project examples")
        print("✅ Have reduced debug output for better performance")
    else:
        print("⚠️ SOME ISSUES REMAIN - Check individual test results above")
    
    print("=" * 80)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
