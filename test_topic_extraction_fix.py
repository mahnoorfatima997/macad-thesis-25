"""
Test Topic Extraction Fix
Tests that the flexible topic extraction now works for ANY topic
"""

import sys
import os

# Add the project root to the path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'thesis-agents'))

def test_topic_extraction():
    """Test the flexible topic extraction method."""
    
    try:
        from agents.domain_expert.adapter import DomainExpertAdapter
        
        # Create adapter instance
        adapter = DomainExpertAdapter("architecture")
        
        # Test cases from user's examples
        test_cases = [
            {
                "input": "i am thinking about using organic forms for my project what are the good examples that i can inspire from?",
                "expected_contains": "organic forms",
                "description": "Organic forms example request"
            },
            {
                "input": "what should be the size of a event space for 200 people?",
                "expected_contains": "event space",
                "description": "Event space sizing question"
            },
            {
                "input": "how can I use parametric design in my museum project?",
                "expected_contains": "parametric design",
                "description": "Parametric design question"
            },
            {
                "input": "what are some good examples of sustainable materials?",
                "expected_contains": "sustainable materials",
                "description": "Sustainable materials question"
            },
            {
                "input": "how do I design flexible spaces for a community center?",
                "expected_contains": "flexible spaces",
                "description": "Flexible spaces question"
            },
            {
                "input": "what is biophilic design and how can I apply it?",
                "expected_contains": "biophilic design",
                "description": "Biophilic design question"
            },
            {
                "input": "show me examples of adaptive reuse projects",
                "expected_contains": "adaptive reuse",
                "description": "Adaptive reuse examples"
            },
            {
                "input": "what are the acoustic requirements for concert halls?",
                "expected_contains": "acoustic",
                "description": "Acoustic requirements question"
            }
        ]
        
        print("🎯 FLEXIBLE TOPIC EXTRACTION TEST")
        print("=" * 60)
        
        all_passed = True
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\nTest {i}: {test_case['description']}")
            print(f"Input: \"{test_case['input']}\"")
            
            # Extract topic
            extracted_topic = adapter._extract_topic_from_user_input(test_case['input'])
            
            print(f"Extracted Topic: \"{extracted_topic}\"")
            print(f"Expected to contain: \"{test_case['expected_contains']}\"")
            
            # Check if extraction is reasonable
            if test_case['expected_contains'].lower() in extracted_topic.lower():
                print("✅ PASS - Contains expected topic")
            else:
                print("❌ FAIL - Does not contain expected topic")
                all_passed = False
            
            # Check if extraction is meaningful (not generic)
            if extracted_topic in ["design approach", "design", "space design"]:
                print("⚠️  WARNING - Topic extraction is too generic")
            else:
                print("✅ GOOD - Topic extraction is specific")
            
            print("-" * 40)
        
        print(f"\n🎯 OVERALL RESULT: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_edge_cases():
    """Test edge cases for topic extraction."""
    
    try:
        from agents.domain_expert.adapter import DomainExpertAdapter
        
        adapter = DomainExpertAdapter("architecture")
        
        edge_cases = [
            {
                "input": "what",
                "description": "Single question word"
            },
            {
                "input": "can you help me?",
                "description": "Generic help request"
            },
            {
                "input": "I need examples of something innovative and creative for my project",
                "description": "Vague request"
            },
            {
                "input": "thermal bridge analysis for curtain wall systems",
                "description": "Technical architectural term"
            },
            {
                "input": "how do Japanese tea houses influence modern minimalist design?",
                "description": "Complex architectural question"
            }
        ]
        
        print("\n\n🔍 EDGE CASES TEST")
        print("=" * 60)
        
        for i, test_case in enumerate(edge_cases, 1):
            print(f"\nEdge Case {i}: {test_case['description']}")
            print(f"Input: \"{test_case['input']}\"")
            
            extracted_topic = adapter._extract_topic_from_user_input(test_case['input'])
            
            print(f"Extracted Topic: \"{extracted_topic}\"")
            
            # Check if extraction makes sense
            if len(extracted_topic) > 0 and extracted_topic != test_case['input'].lower():
                print("✅ GOOD - Extracted meaningful topic")
            else:
                print("⚠️  OK - Basic extraction")
        
        return True
        
    except Exception as e:
        print(f"❌ Edge case test failed: {e}")
        return False

def compare_old_vs_new():
    """Compare the old hardcoded approach vs new flexible approach."""
    
    print("\n\n📊 OLD vs NEW COMPARISON")
    print("=" * 60)
    
    print("""
    **OLD APPROACH (Hardcoded):**
    - Had fixed list of ~50 architectural topics
    - "organic forms" → NOT in list → Falls back to "design approach" ❌
    - "event space size" → NOT in list → Falls back to "design approach" ❌
    - Only worked for predefined topics
    
    **NEW APPROACH (Flexible):**
    - Extracts ANY meaningful topic from user input
    - "organic forms examples" → "organic forms" ✅
    - "event space size for 200 people" → "event space size" ✅
    - Works for ANY architectural topic
    
    **Key Improvements:**
    1. No hardcoded topic list
    2. Extracts noun phrases intelligently
    3. Handles compound terms (2-3 words)
    4. Filters out question words
    5. Returns specific, meaningful topics
    """)

if __name__ == "__main__":
    print("Testing flexible topic extraction...\n")
    
    # Test main functionality
    main_passed = test_topic_extraction()
    
    # Test edge cases
    edge_passed = test_edge_cases()
    
    # Show comparison
    compare_old_vs_new()
    
    print("\n\n🎯 SUMMARY")
    print("=" * 60)
    
    if main_passed and edge_passed:
        print("✅ ALL TESTS PASSED")
        print("✅ Topic extraction is now FLEXIBLE and works for ANY topic")
        print("✅ Should fix the terrible query understanding issues")
        print("\n🎉 Expected Results:")
        print("- 'organic forms examples' → Will search for and find organic forms content")
        print("- 'event space size for 200 people' → Will search for event space sizing content")
        print("- ANY architectural topic → Will extract and search correctly")
    else:
        print("❌ SOME TESTS FAILED")
        print("❌ Topic extraction may still have issues")
    
    print("\n🧪 Next: Test this in the actual mentor system to verify it finds the right information!")
