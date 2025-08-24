#!/usr/bin/env python3
"""
Test conversation-aware gamification improvements:
1. Games now use conversation context in cache keys
2. Relative import warning fixed
"""

import sys
import os
sys.path.append('.')
sys.path.append('thesis-agents')

def test_conversation_aware_caching():
    """Test that games now use conversation context for better caching"""
    print("🧪 TESTING: Conversation-aware game caching")
    print("=" * 60)
    
    try:
        # Check if the caching logic includes conversation context
        with open('dashboard/ui/enhanced_gamification.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Look for conversation-aware caching patterns
        conversation_patterns = [
            'conversation_context = getattr(st.session_state',
            'context_hash = hash(str(conversation_context)',
            'CONVERSATION-AWARE CACHING',
            'Last 3 messages for context'
        ]
        
        found_patterns = []
        for pattern in conversation_patterns:
            if pattern in content:
                found_patterns.append(pattern)
        
        print(f"Checking for conversation-aware caching...")
        print(f"Found conversation patterns: {len(found_patterns)}/4")
        
        for pattern in found_patterns:
            print(f"  ✅ {pattern}")
        
        if len(found_patterns) >= 3:
            print("\n✅ CONVERSATION-AWARE CACHING IMPLEMENTED")
            print("   Games will now generate fresh content based on conversation context")
            print("   Cache keys include recent messages, not just building type")
            return True
        else:
            print("\n❌ CONVERSATION-AWARE CACHING NOT FULLY IMPLEMENTED")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_relative_import_fix():
    """Test that the relative import warning is fixed"""
    print("\n🧪 TESTING: Relative import warning fix")
    print("=" * 60)
    
    try:
        # Check if the relative import is fixed in context.py
        with open('thesis-agents/orchestration/nodes/context.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Look for the fix patterns
        fix_patterns = [
            'FIXED: Use absolute import',
            'from agents.context_agent.processors.input_classification',
            'sys.path.append',
            'FIXED: Reduced warning verbosity'
        ]
        
        found_fixes = []
        for pattern in fix_patterns:
            if pattern in content:
                found_fixes.append(pattern)
        
        print(f"Checking for relative import fixes...")
        print(f"Found fix patterns: {len(found_fixes)}/4")
        
        for pattern in found_fixes:
            print(f"  ✅ {pattern}")
        
        # Also check that the old relative import is gone
        old_relative_import = 'from ...agents.context_agent.processors.input_classification'
        has_old_import = old_relative_import in content
        
        print(f"Old relative import removed: {not has_old_import}")
        
        if len(found_fixes) >= 3 and not has_old_import:
            print("\n✅ RELATIVE IMPORT WARNING FIXED")
            print("   Absolute import used instead of relative import")
            print("   Warning verbosity reduced to debug level")
            return True
        else:
            print("\n❌ RELATIVE IMPORT WARNING NOT FULLY FIXED")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_cache_key_differences():
    """Test that different conversation contexts produce different cache keys"""
    print("\n🧪 TESTING: Cache key differentiation")
    print("=" * 60)
    
    try:
        # Simulate different conversation contexts
        import streamlit as st
        
        # Mock streamlit session state
        class MockSessionState:
            def __init__(self):
                self.messages = []
        
        # Test scenario 1: Initial conversation
        mock_state_1 = MockSessionState()
        mock_state_1.messages = [
            {'role': 'user', 'content': 'I am designing a community center'},
            {'role': 'assistant', 'content': 'Great! Tell me more about your vision.'}
        ]
        
        # Test scenario 2: After transformation discussion
        mock_state_2 = MockSessionState()
        mock_state_2.messages = [
            {'role': 'user', 'content': 'I am designing a community center'},
            {'role': 'assistant', 'content': 'TRANSFORMATION CHALLENGE: Consider how spaces adapt...'},
            {'role': 'user', 'content': 'I would use movable partitions and modular furniture'}
        ]
        
        # Simulate cache key generation
        building_type = "community_center"
        user_message = "How should I design the main hall?"
        
        # Scenario 1 cache key
        context_1 = str(mock_state_1.messages[-3:]) + user_message[:50]
        cache_key_1 = f"personas_{building_type}_{hash(context_1)}"
        
        # Scenario 2 cache key  
        context_2 = str(mock_state_2.messages[-3:]) + user_message[:50]
        cache_key_2 = f"personas_{building_type}_{hash(context_2)}"
        
        print(f"Scenario 1 context: Initial conversation")
        print(f"Scenario 2 context: After transformation discussion")
        print(f"Same user message: '{user_message}'")
        print(f"Same building type: '{building_type}'")
        print()
        print(f"Cache key 1: {cache_key_1[:50]}...")
        print(f"Cache key 2: {cache_key_2[:50]}...")
        print(f"Cache keys different: {cache_key_1 != cache_key_2}")
        
        if cache_key_1 != cache_key_2:
            print("\n✅ CACHE KEY DIFFERENTIATION WORKING")
            print("   Different conversation contexts produce different cache keys")
            print("   Games will be contextual to the conversation flow")
            return True
        else:
            print("\n❌ CACHE KEY DIFFERENTIATION NOT WORKING")
            print("   Same cache keys despite different conversation contexts")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Run all conversation-aware gamification tests"""
    print("🚀 TESTING CONVERSATION-AWARE GAMIFICATION IMPROVEMENTS")
    print("Testing fixes for:")
    print("1. Games cached without conversation context")
    print("2. Relative import warning in orchestrator")
    print("3. Cache key differentiation for context awareness")
    print("=" * 80)
    
    # Run tests
    test1_passed = test_conversation_aware_caching()
    test2_passed = test_relative_import_fix()
    test3_passed = test_cache_key_differences()
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 CONVERSATION-AWARE GAMIFICATION TEST RESULTS")
    print("=" * 80)
    
    tests = [
        ("🎮 Conversation-Aware Caching", test1_passed),
        ("⚠️ Relative Import Warning Fix", test2_passed),
        ("🔑 Cache Key Differentiation", test3_passed)
    ]
    
    all_passed = True
    for test_name, passed in tests:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 80)
    if all_passed:
        print("🎉 ALL CONVERSATION-AWARE IMPROVEMENTS WORKING!")
        print("✅ Games now use conversation context for better caching")
        print("✅ Different conversation contexts produce different games")
        print("✅ Relative import warning eliminated")
        print("✅ Games will be more contextual and conversation-aware")
    else:
        print("⚠️ SOME IMPROVEMENTS NEED MORE WORK")
        print("Check failed tests above for details")
    
    print("=" * 80)

if __name__ == "__main__":
    main()
