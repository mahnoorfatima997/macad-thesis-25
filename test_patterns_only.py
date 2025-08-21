"""
Test Gamification Trigger Patterns Only
Tests just the pattern matching logic without requiring API keys
"""

def test_pattern_matching():
    """Test pattern matching directly."""
    
    # Test messages from user examples
    test_messages = [
        "I think I should start with thinking about how a community member feel in this building",
        "How does my design feel from a teenager's perspective", 
        "I need fresh ideas for my design",
        "help me see this from a different angle",
        "how would a visitor feel when they enter my community center?",
        "The building should have good lighting"  # Should NOT trigger
    ]
    
    # Current trigger patterns from the code
    role_play_patterns = [
        'how would a visitor feel', 'how would', 'what would', 'from the perspective of',
        'how do users feel', 'what would an elderly person', 'what would a child',
        'how a', 'feel in this', 'feel when they', 'feel in the', 'experience in',
        'member feel', 'user feel', 'visitor feel', 'person feel',
        'from a', 'as a', 'like a', 'perspective', "'s perspective",
        'teenager\'s perspective', 'child\'s perspective', 'user\'s perspective'
    ]
    
    perspective_shift_patterns = [
        'help me see this from a different angle', 'different angle', 'see this differently',
        'think about this differently', 'different perspective', 'another way to think',
        'alternative viewpoint', 'fresh perspective',
        'different angle', 'differently', 'another way', 'alternative', 
        'fresh perspective', 'new perspective', 'see this', 'think about this'
    ]
    
    constraint_patterns = [
        'i\'m stuck on', 'stuck on', 'having trouble', 'not sure how',
        'i need fresh ideas', 'need fresh ideas', 'fresh ideas', 'new ideas',
        'creative ideas', 'need ideas', 'ideas for', 'inspire', 'inspiration',
        'stuck', 'help me think', 'new approach', 'different approach'
    ]
    
    curiosity_patterns = ['i wonder what would happen', 'what if', 'i wonder']
    
    overconfidence_patterns = [
        'this seems pretty easy', 'this is easy', 'i already know exactly',
        'i already know', 'that\'s obvious', 'simple', 'basic'
    ]
    
    low_engagement_responses = ['ok', 'yes', 'sure', 'fine', 'alright', 'cool', 'maybe']
    
    print("🎮 GAMIFICATION TRIGGER PATTERN TEST")
    print("=" * 60)
    
    for i, message in enumerate(test_messages, 1):
        print(f"\nTest {i}: \"{message}\"")
        message_lower = message.lower().strip()
        
        # Test each pattern set
        triggers = []
        
        # Role-play patterns
        role_matches = [p for p in role_play_patterns if p in message_lower]
        if role_matches:
            triggers.append(f"Role-play: {role_matches}")
        
        # Perspective shift patterns
        perspective_matches = [p for p in perspective_shift_patterns if p in message_lower]
        if perspective_matches:
            triggers.append(f"Perspective: {perspective_matches}")
        
        # Constraint patterns
        constraint_matches = [p for p in constraint_patterns if p in message_lower]
        if constraint_matches:
            triggers.append(f"Constraint: {constraint_matches}")
        
        # Curiosity patterns
        curiosity_matches = [p for p in curiosity_patterns if p in message_lower]
        if curiosity_matches:
            triggers.append(f"Curiosity: {curiosity_matches}")
        
        # Overconfidence patterns
        overconfidence_matches = [p for p in overconfidence_patterns if p in message_lower]
        if overconfidence_matches:
            triggers.append(f"Overconfidence: {overconfidence_matches}")
        
        # Low engagement patterns
        if message_lower in low_engagement_responses:
            triggers.append("Low engagement")
        
        # Results
        if triggers:
            print(f"  ✅ TRIGGERS GAMIFICATION")
            for trigger in triggers:
                print(f"    - {trigger}")
        else:
            print(f"  ❌ NO GAMIFICATION TRIGGERED")
            
            # Analyze why it didn't trigger
            print(f"    🔍 Analysis:")
            print(f"      Message: '{message_lower}'")
            
            # Check for partial matches
            partial_role = [p for p in role_play_patterns if any(word in message_lower for word in p.split())]
            if partial_role:
                print(f"      Partial role-play matches: {partial_role}")
            
            partial_perspective = [p for p in perspective_shift_patterns if any(word in message_lower for word in p.split())]
            if partial_perspective:
                print(f"      Partial perspective matches: {partial_perspective}")
            
            partial_constraint = [p for p in constraint_patterns if any(word in message_lower for word in p.split())]
            if partial_constraint:
                print(f"      Partial constraint matches: {partial_constraint}")

def analyze_specific_failures():
    """Analyze why specific user messages are failing."""
    
    print("\n\n🔍 SPECIFIC FAILURE ANALYSIS")
    print("=" * 60)
    
    failures = [
        {
            "message": "I think I should start with thinking about how a community member feel in this building",
            "should_match": "Role-play (contains 'how a' and 'member feel')",
            "analysis": "Should match 'how a' and 'member feel' patterns"
        },
        {
            "message": "How does my design feel from a teenager's perspective",
            "should_match": "Role-play (contains 'perspective' and 'from a')",
            "analysis": "Should match 'perspective' and 'from a' patterns"
        },
        {
            "message": "I need fresh ideas for my design",
            "should_match": "Constraint (contains 'fresh ideas')",
            "analysis": "Should match 'fresh ideas' pattern"
        }
    ]
    
    for failure in failures:
        print(f"\nAnalyzing: \"{failure['message']}\"")
        print(f"Should match: {failure['should_match']}")
        
        message_lower = failure['message'].lower()
        
        # Check specific patterns
        if 'how a' in message_lower:
            print(f"  ✅ Contains 'how a'")
        if 'member feel' in message_lower:
            print(f"  ✅ Contains 'member feel'")
        if 'perspective' in message_lower:
            print(f"  ✅ Contains 'perspective'")
        if 'from a' in message_lower:
            print(f"  ✅ Contains 'from a'")
        if 'fresh ideas' in message_lower:
            print(f"  ✅ Contains 'fresh ideas'")
        
        print(f"  Analysis: {failure['analysis']}")

def suggest_pattern_improvements():
    """Suggest improvements to the trigger patterns."""
    
    print("\n\n💡 PATTERN IMPROVEMENT SUGGESTIONS")
    print("=" * 60)
    
    print("""
Based on the user examples, here are the patterns that should be added:

ROLE-PLAY PATTERNS (add these):
- 'thinking about how'
- 'how.*feel' (regex pattern)
- 'member.*feel' (regex pattern)
- 'design feel'
- 'feel from'

PERSPECTIVE PATTERNS (add these):
- 'from.*perspective' (regex pattern)
- 'teenager.*perspective' (regex pattern)
- 'design.*perspective' (regex pattern)

CONSTRAINT PATTERNS (add these):
- 'need.*ideas' (regex pattern)
- 'fresh.*ideas' (regex pattern)
- 'ideas.*design' (regex pattern)

CURRENT ISSUE:
The patterns are too specific. User language is more varied.
Need broader patterns that catch the intent, not exact phrases.

RECOMMENDED FIX:
Use regex patterns or broader keyword matching instead of exact phrase matching.
    """)

if __name__ == "__main__":
    print("Testing gamification trigger patterns...\n")
    
    test_pattern_matching()
    analyze_specific_failures()
    suggest_pattern_improvements()
    
    print("\n\n🎯 CONCLUSION")
    print("=" * 60)
    print("The trigger patterns need to be broader and more flexible")
    print("to catch the natural language users actually use.")
    print("Consider using regex patterns or keyword-based matching.")
