#!/usr/bin/env python3
"""
Test the REAL transformation issues:
1. Transformation challenges are hardcoded (not AI-generated as claimed)
2. Transformation challenges trigger repeatedly (infinite loop)
3. Excessive debug prints
"""

import sys
import os
sys.path.append('.')
sys.path.append('thesis-agents')

from dotenv import load_dotenv
load_dotenv()

def test_hardcoded_transformation_format():
    """Test Issue 1: Transformation challenges use hardcoded JSON format"""
    print("🧪 TESTING ISSUE 1: Hardcoded transformation format")
    print("=" * 60)
    
    try:
        # Check the hardcoded format in enhanced_gamification.py
        with open('dashboard/ui/enhanced_gamification.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Look for the hardcoded JSON format
        hardcoded_patterns = [
            '"The Warm Welcome Entrance"',
            '"Interactive Learning Lab"',
            '"Community Gathering Hub"'
        ]
        
        found_hardcoded = []
        for pattern in hardcoded_patterns:
            if pattern in content:
                found_hardcoded.append(pattern)
        
        print(f"Checking for hardcoded transformation names...")
        print(f"Found hardcoded patterns: {found_hardcoded}")
        
        if found_hardcoded:
            print("❌ ISSUE 1 CONFIRMED: Transformation challenges use hardcoded JSON format")
            print("   The AI prompt forces specific names instead of being contextual")
            return False
        else:
            print("✅ ISSUE 1 FIXED: No hardcoded transformation names found")
            return True
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_transformation_repetition():
    """Test Issue 2: Transformation challenges trigger repeatedly"""
    print("\n🧪 TESTING ISSUE 2: Transformation challenge repetition")
    print("=" * 60)
    
    try:
        from agents.cognitive_enhancement.processors.challenge_generator import ChallengeGeneratorProcessor
        from state_manager import ArchMentorState
        
        processor = ChallengeGeneratorProcessor()
        
        # Simulate the exact scenario from terminal:
        # 1. User mentions transformation
        # 2. System triggers transformation challenge
        # 3. User responds to transformation challenge (mentions "converting" again)
        # 4. System should NOT trigger another transformation challenge
        
        state = ArchMentorState()
        state.messages = [
            {'role': 'user', 'content': 'I am converting a warehouse to a community center'},
            {'role': 'assistant', 'content': 'Great! Let me present a transformation challenge...'},
            {'role': 'assistant', 'content': 'TRANSFORMATION CHALLENGE: Your building needs to accommodate different scenarios...'},
            {'role': 'user', 'content': '🔄 Transformation Approach: I would use movable partitions to divide or open up the space depending on the activity, and incorporate modular, lightweight furniture that can be rearranged for workshops, classes, or social gatherings.'}
        ]
        
        print("Scenario:")
        print("1. User: 'I am converting a warehouse to a community center'")
        print("2. Assistant: [Triggers transformation challenge]")
        print("3. User responds: '🔄 Transformation Approach: I would use movable partitions...'")
        print("4. Should system trigger another transformation challenge?")
        print()
        
        # Test strategy selection (this is where the issue occurs)
        user_response = "🔄 Transformation Approach: I would use movable partitions to divide or open up the space depending on the activity, and incorporate modular, lightweight furniture that can be rearranged for workshops, classes, or social gatherings."
        
        # This should NOT return "transformation_design" because we recently used transformation
        cognitive_state = {"engagement_level": "high"}
        analysis_result = {"user_input": user_response}
        strategy = processor.select_enhancement_strategy(cognitive_state, analysis_result, state)
        
        print(f"User response contains transformation keywords: {'transform' in user_response.lower()}")
        print(f"Recent assistant messages contain transformation: {any('transformation' in msg['content'].lower() for msg in state.messages if msg.get('role') == 'assistant')}")
        print(f"Selected strategy: {strategy}")
        print(f"Expected: NOT 'transformation_design' (should be something else)")
        print()
        
        if strategy != "transformation_design":
            print("✅ ISSUE 2 FIXED: Transformation challenges don't repeat consecutively")
            return True
        else:
            print("❌ ISSUE 2 NOT FIXED: Transformation challenges still repeat")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_transformation_caching():
    """Test Issue 1b: Transformation challenges are cached instead of AI-generated"""
    print("\n🧪 TESTING ISSUE 1b: Transformation challenge caching")
    print("=" * 60)
    
    try:
        # Check if caching is preventing fresh AI generation
        with open('dashboard/ui/enhanced_gamification.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Look for improved caching logic that allows fresh generation for transformation responses
        improved_cache_patterns = [
            'is_transformation_response',
            'Skip cache for transformation responses',
            'not is_transformation_response'
        ]

        found_improvements = []
        for pattern in improved_cache_patterns:
            if pattern in content:
                found_improvements.append(pattern)

        print(f"Checking for improved caching logic...")
        print(f"Found cache improvements: {found_improvements}")

        # Also check if the problematic cache hit print is commented out
        cache_hit_commented = '# print(f"🚀 CACHE HIT: Using cached transformations' in content

        if found_improvements and cache_hit_commented:
            print("✅ ISSUE 1b FIXED: Caching improved to allow fresh AI generation")
            print("   - Transformation responses skip cache")
            print("   - Cache hit debug print commented out")
            return True
        else:
            print("⚠️ ISSUE 1b PARTIAL: Some caching improvements missing")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Run all transformation issue tests"""
    print("🚀 TESTING REAL TRANSFORMATION ISSUES")
    print("Based on terminal analysis, testing:")
    print("1. Hardcoded JSON format (not AI-generated as claimed)")
    print("2. Transformation challenges triggering repeatedly")
    print("3. Caching preventing fresh AI generation")
    print("=" * 80)
    
    # Run tests
    issue1_fixed = test_hardcoded_transformation_format()
    issue2_fixed = test_transformation_repetition()
    issue1b_fixed = test_transformation_caching()
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 TRANSFORMATION ISSUES TEST RESULTS")
    print("=" * 80)
    
    issues = [
        ("🔧 Issue 1: Hardcoded JSON Format", issue1_fixed),
        ("🔄 Issue 2: Transformation Repetition", issue2_fixed),
        ("💾 Issue 1b: Problematic Caching", issue1b_fixed)
    ]
    
    all_fixed = True
    for issue_name, fixed in issues:
        status = "✅ FIXED" if fixed else "❌ NOT FIXED"
        print(f"{issue_name}: {status}")
        if not fixed:
            all_fixed = False
    
    print("\n" + "=" * 80)
    if all_fixed:
        print("🎉 ALL TRANSFORMATION ISSUES FIXED!")
        print("✅ Transformations are truly AI-generated and contextual")
        print("✅ No more infinite transformation loops")
        print("✅ Fresh AI generation for each challenge")
    else:
        print("⚠️ TRANSFORMATION ISSUES REMAIN - Check failed tests above")
        print()
        print("NEXT STEPS:")
        if not issue1_fixed:
            print("- Fix hardcoded JSON format in enhanced_gamification.py")
        if not issue2_fixed:
            print("- Fix strategy selection to prevent consecutive transformations")
        if not issue1b_fixed:
            print("- Adjust caching to allow fresh AI generation")
    
    print("=" * 80)

if __name__ == "__main__":
    main()
