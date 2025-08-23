"""
Test Domain Expert Fix
Tests that the domain expert now uses the correct topic extraction for database and web searches
"""

import sys
import os

# Add the project root to the path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'thesis-agents'))

def test_topic_extraction_integration():
    """Test that the domain expert uses the fixed topic extraction."""
    
    try:
        from agents.domain_expert.adapter import DomainExpertAgent
        
        # Create domain expert instance
        domain_expert = DomainExpertAgent("architecture")
        
        # Test cases from user's problematic examples
        test_cases = [
            {
                "user_input": "i am thinking about using organic forms for my project what are the good examples that i can inspire from?",
                "expected_topic": "organic forms",
                "expected_db_query_contains": "organic forms",
                "expected_web_query_contains": "organic forms",
                "description": "Organic forms example request"
            },
            {
                "user_input": "what should be the size of a event space for 200 people?",
                "expected_topic": "event space",
                "expected_db_query_contains": "event space",
                "expected_web_query_contains": "event space",
                "description": "Event space sizing question"
            },
            {
                "user_input": "show me examples of parametric design in museums",
                "expected_topic": "parametric design",
                "expected_db_query_contains": "parametric design",
                "expected_web_query_contains": "parametric design",
                "description": "Parametric design examples"
            }
        ]
        
        print("🔧 DOMAIN EXPERT TOPIC EXTRACTION INTEGRATION TEST")
        print("=" * 70)
        
        all_passed = True
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\nTest {i}: {test_case['description']}")
            print(f"Input: \"{test_case['user_input']}\"")
            
            # Test topic extraction
            extracted_topic = domain_expert._extract_topic_from_user_input(test_case['user_input'])
            print(f"Extracted Topic: \"{extracted_topic}\"")
            
            # Check if topic extraction is correct
            if test_case['expected_topic'].lower() in extracted_topic.lower():
                print("✅ Topic extraction CORRECT")
            else:
                print(f"❌ Topic extraction WRONG - Expected: {test_case['expected_topic']}, Got: {extracted_topic}")
                all_passed = False
            
            # Test database query creation
            db_query = domain_expert._create_specific_db_query_with_topic(
                extracted_topic, "community center", "general_examples"
            )
            print(f"DB Query: \"{db_query}\"")
            
            if test_case['expected_db_query_contains'].lower() in db_query.lower():
                print("✅ DB query contains expected topic")
            else:
                print(f"❌ DB query WRONG - Expected to contain: {test_case['expected_db_query_contains']}")
                all_passed = False
            
            # Test web query creation
            web_query = domain_expert._create_specific_web_query_with_topic(
                extracted_topic, "community center", "general_examples"
            )
            print(f"Web Query: \"{web_query}\"")
            
            if test_case['expected_web_query_contains'].lower() in web_query.lower():
                print("✅ Web query contains expected topic")
            else:
                print(f"❌ Web query WRONG - Expected to contain: {test_case['expected_web_query_contains']}")
                all_passed = False
            
            print("-" * 50)
        
        print(f"\n🎯 OVERALL RESULT: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_before_vs_after():
    """Show the before vs after comparison."""
    
    print("\n\n📊 BEFORE vs AFTER COMPARISON")
    print("=" * 70)
    
    print("""
    **BEFORE (Broken):**
    
    User: "organic forms examples"
    ├── Topic Extraction: "design approach" (generic fallback) ❌
    ├── DB Query: "community center design approach" ❌
    ├── Web Query: "community center design approach" ❌
    └── Result: Generic community center content ❌
    
    User: "event space size for 200 people"
    ├── Topic Extraction: "design approach" (generic fallback) ❌
    ├── DB Query: "community center design approach" ❌
    ├── Web Query: "community center design approach" ❌
    └── Result: Generic community center content ❌
    
    **AFTER (Fixed):**
    
    User: "organic forms examples"
    ├── Topic Extraction: "organic forms" ✅
    ├── DB Query: "organic forms community center" ✅
    ├── Web Query: "community center organic forms architecture design" ✅
    └── Result: Specific organic forms content ✅
    
    User: "event space size for 200 people"
    ├── Topic Extraction: "event space" ✅
    ├── DB Query: "event space community center" ✅
    ├── Web Query: "community center event space architecture design" ✅
    └── Result: Specific event space sizing content ✅
    """)

def show_technical_changes():
    """Show the technical changes made."""
    
    print("\n\n🔧 TECHNICAL CHANGES MADE")
    print("=" * 70)
    
    print("""
    **1. Fixed Topic Extraction (_extract_topic_from_user_input):**
    - Removed hardcoded topic list
    - Added flexible phrase extraction
    - Prioritizes architectural compound terms
    - Handles ANY topic, not just predefined ones
    
    **2. Updated Database Search:**
    - Changed: _create_specific_db_query(user_input, ...)
    - To: _create_specific_db_query_with_topic(user_topic, ...)
    - Now uses extracted topic directly
    
    **3. Updated Web Search:**
    - Changed: _create_specific_web_query(user_input, ...)
    - To: _create_specific_web_query_with_topic(user_topic, ...)
    - Now uses extracted topic directly
    
    **4. Query Construction:**
    - DB: "{topic} {building_type}" (e.g., "organic forms community center")
    - Web: "{building_type} {topic} architecture design"
    - Much more specific and targeted
    
    **Result:** Domain expert now searches for the RIGHT content!
    """)

if __name__ == "__main__":
    print("Testing domain expert topic extraction integration...\n")
    
    # Test the integration
    main_passed = test_topic_extraction_integration()
    
    # Show comparisons
    show_before_vs_after()
    show_technical_changes()
    
    print("\n\n🎯 SUMMARY")
    print("=" * 70)
    
    if main_passed:
        print("✅ DOMAIN EXPERT INTEGRATION FIXED!")
        print("✅ Topic extraction now works correctly")
        print("✅ Database searches use extracted topics")
        print("✅ Web searches use extracted topics")
        print("✅ Should fix the terrible query understanding")
        print("\n🎉 Expected Results:")
        print("- 'organic forms examples' → Searches for organic forms content")
        print("- 'event space size for 200 people' → Searches for event space content")
        print("- No more generic community center responses!")
        print("- Specific, relevant content for user's actual questions")
    else:
        print("❌ SOME INTEGRATION TESTS FAILED")
        print("❌ May need further debugging")
    
    print("\n🧪 Next: Test this in the actual mentor system to verify it finds relevant content!")
