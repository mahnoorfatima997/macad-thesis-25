#!/usr/bin/env python3
"""
Test to check if the enhanced design_guidance_patterns are working correctly.
"""

def test_design_guidance_patterns():
    """Test the enhanced design guidance patterns."""
    print("🔍 Testing Enhanced Design Guidance Patterns...")
    
    # The enhanced patterns from the code
    design_guidance_patterns = [
        "can you help me", "could you help me", "i need help with",
        "i want help with", "can you guide me", "could you guide me",
        "i need guidance", "i want guidance", "can you advise me",
        "could you advise me", "i need advice", "i want advice",
        "can you suggest", "could you suggest", "i need suggestions",
        "i want suggestions", "what should i", "how should i",
        # ENHANCED: More flexible patterns to catch variations
        "what should my", "how should my", "what should we", "how should we",
        "what approach should", "how approach should", "what strategy should",
        "how strategy should", "what method should", "how method should",
        "curious how", "wondering how", "thinking about how",
        "not sure how", "unsure how", "confused about how",
        "need help organizing", "want help organizing", "help me organize",
        "guidance on", "advice on", "suggestions for", "help with",
        # ENHANCED: More specific patterns for approach/strategy questions
        "what should my approach", "how should my approach",
        "what approach should i", "how approach should i",
        "what is my approach", "how is my approach",
        "what would be my approach", "how would be my approach",
        "what do you think my approach", "how do you think my approach",
        "approach should", "strategy should", "method should",
        "organize my", "organize the", "organize spaces",
        "organize around", "organize courtyards", "organize gardens"
    ]
    
    # Test the problematic input
    test_input = "I am curious how I should organize my spaces around those courtyards and gardens. What should be my approach?"
    test_input_lower = test_input.lower()
    
    print(f"\n📋 Testing input: {test_input}")
    print(f"📋 Input (lowercase): {test_input_lower}")
    
    # Check each pattern
    matched_patterns = []
    for pattern in design_guidance_patterns:
        if pattern in test_input_lower:
            print(f"  ✅ MATCHED pattern: '{pattern}'")
            matched_patterns.append(pattern)
        else:
            print(f"  ❌ NO MATCH for pattern: '{pattern}'")
    
    if matched_patterns:
        print(f"\n🎯 SUCCESS: Found {len(matched_patterns)} matching patterns:")
        for pattern in matched_patterns:
            print(f"  - '{pattern}'")
        return True
    else:
        print("\n❌ FAILURE: NO PATTERNS MATCHED")
        return False

if __name__ == "__main__":
    test_design_guidance_patterns()
