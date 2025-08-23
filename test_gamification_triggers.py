"""
Gamification Trigger Test Script
Tests if gamification triggers are working correctly with real user examples
"""

import streamlit as st
import sys
import os
import asyncio

# Add the project root to the path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from thesis_agents.agents.cognitive_enhancement.processors.challenge_generator import ChallengeGeneratorProcessor
from state_manager import ArchMentorState

st.set_page_config(
    page_title="🎮 Gamification Trigger Test",
    page_icon="🎮",
    layout="wide"
)

st.title("🎮 Gamification Trigger Test Script")
st.markdown("**Testing if gamification triggers are working correctly**")

# Initialize processor
if 'challenge_processor' not in st.session_state:
    st.session_state.challenge_processor = ChallengeGeneratorProcessor()

def create_test_state(user_messages: list, building_type: str = "community center") -> ArchMentorState:
    """Create a test state with conversation history."""
    state = ArchMentorState()
    
    # Add conversation history
    messages = []
    for i, msg in enumerate(user_messages):
        if i % 2 == 0:  # User messages
            messages.append({"role": "user", "content": msg})
        else:  # Assistant messages
            messages.append({"role": "assistant", "content": msg})
    
    state.messages = messages
    state.current_design_brief = f"Design a {building_type} that serves the community"
    return state

def test_gamification_trigger(user_message: str, context_messages: list = None) -> dict:
    """Test if a user message triggers gamification."""
    
    # Create state with context
    all_messages = (context_messages or []) + [user_message]
    state = create_test_state(all_messages)
    
    # Test the trigger logic directly
    processor = st.session_state.challenge_processor
    
    # Check if gamification should be applied
    should_gamify = processor._should_apply_gamification(state, "user_perspective", "perspective_challenge")
    
    return {
        "user_message": user_message,
        "should_trigger_gamification": should_gamify,
        "latest_message": user_message.lower(),
        "state_messages_count": len(state.messages)
    }

# Test Cases from User's Examples
st.header("🧪 Real User Examples Test")

user_test_cases = [
    {
        "name": "Community Member Feeling",
        "message": "I think I should start with thinking about how a community member feel in this building",
        "expected": "Should trigger Role Play game",
        "trigger_type": "perspective_challenge"
    },
    {
        "name": "Teenager's Perspective", 
        "message": "How does my design feel from a teenager's perspective",
        "expected": "Should trigger Perspective Wheel game",
        "trigger_type": "perspective_challenge"
    },
    {
        "name": "Fresh Ideas Request",
        "message": "I need fresh ideas for my design", 
        "expected": "Should trigger Creative Challenge game",
        "trigger_type": "alternative_challenge"
    },
    {
        "name": "Different Angle Request",
        "message": "help me see this from a different angle",
        "expected": "Should trigger Perspective Shift game", 
        "trigger_type": "perspective_challenge"
    },
    {
        "name": "User Experience Question",
        "message": "how would a visitor feel when they enter my community center?",
        "expected": "Should trigger Role Play game",
        "trigger_type": "perspective_challenge"
    }
]

st.markdown("**Testing real user messages that should trigger gamification:**")

for i, test_case in enumerate(user_test_cases):
    st.markdown(f"### Test {i+1}: {test_case['name']}")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"**Message:** \"{test_case['message']}\"")
        st.markdown(f"**Expected:** {test_case['expected']}")
    
    with col2:
        if st.button(f"🧪 Test #{i+1}", key=f"test_{i}"):
            result = test_gamification_trigger(test_case['message'])
            
            if result['should_trigger_gamification']:
                st.success("✅ TRIGGERS GAMIFICATION")
            else:
                st.error("❌ NO GAMIFICATION TRIGGERED")
            
            # Show debug info
            with st.expander(f"🔍 Debug Info #{i+1}"):
                st.json(result)

# Pattern Analysis
st.header("🔍 Pattern Analysis")

st.markdown("**Let me check what patterns are currently being detected:**")

if st.button("🔍 Analyze Current Trigger Patterns", type="primary"):
    
    # Get the current trigger patterns from the processor
    processor = st.session_state.challenge_processor
    
    st.markdown("**Current Gamification Trigger Logic:**")
    
    # Test each user message against all patterns
    for test_case in user_test_cases:
        message = test_case['message'].lower()
        
        st.markdown(f"### Testing: \"{test_case['message']}\"")
        
        # Check role-play patterns
        role_play_patterns = [
            'how would a visitor feel', 'how would', 'what would', 'from the perspective of',
            'how do users feel', 'what would an elderly person', 'what would a child'
        ]
        
        role_play_match = any(pattern in message for pattern in role_play_patterns)
        st.markdown(f"**Role-play patterns:** {'✅ MATCH' if role_play_match else '❌ NO MATCH'}")
        if role_play_match:
            matches = [p for p in role_play_patterns if p in message]
            st.text(f"  Matched: {matches}")
        
        # Check curiosity patterns
        curiosity_patterns = ['i wonder what would happen', 'what if', 'i wonder']
        curiosity_match = any(pattern in message for pattern in curiosity_patterns)
        st.markdown(f"**Curiosity patterns:** {'✅ MATCH' if curiosity_match else '❌ NO MATCH'}")
        
        # Check perspective shift patterns
        perspective_shift_patterns = [
            'help me see this from a different angle', 'different angle', 'see this differently',
            'think about this differently', 'different perspective', 'another way to think',
            'alternative viewpoint', 'fresh perspective'
        ]
        perspective_match = any(pattern in message for pattern in perspective_shift_patterns)
        st.markdown(f"**Perspective shift patterns:** {'✅ MATCH' if perspective_match else '❌ NO MATCH'}")
        
        # Check creative constraint patterns
        creative_patterns = ['i need ideas', 'fresh ideas', 'new ideas', 'creative ideas', 'stuck', 'help me think']
        creative_match = any(pattern in message for pattern in creative_patterns)
        st.markdown(f"**Creative patterns:** {'✅ MATCH' if creative_match else '❌ NO MATCH'}")
        
        # Overall result
        any_match = role_play_match or curiosity_match or perspective_match or creative_match
        st.markdown(f"**OVERALL RESULT:** {'✅ SHOULD TRIGGER' if any_match else '❌ NO TRIGGER'}")
        
        st.markdown("---")

# Missing Patterns Analysis
st.header("🚨 Missing Patterns Analysis")

st.markdown("""
**Based on your examples, these patterns are missing from the trigger logic:**

1. **"how a community member feel"** → Should match role-play patterns
2. **"from a teenager's perspective"** → Should match perspective patterns  
3. **"I need fresh ideas"** → Should match creative constraint patterns
4. **"feel in this building"** → Should match user experience patterns

**The issue might be:**
- Patterns are too specific (need broader matching)
- Pattern matching is case-sensitive
- Missing key phrases that users actually say
""")

# Suggested Fixes
with st.expander("🔧 Suggested Pattern Fixes"):
    st.markdown("""
    **Add these missing patterns:**
    
    ```python
    # Role-play patterns (add these)
    role_play_patterns = [
        'how would a visitor feel', 'how would', 'what would', 'from the perspective of',
        'how do users feel', 'what would an elderly person', 'what would a child',
        # ADD THESE:
        'how a', 'feel in this', 'feel when they', 'experience in', 'perspective',
        'from a', 'as a', 'like a', 'member feel', 'user feel', 'visitor feel'
    ]
    
    # Creative constraint patterns (add these)  
    creative_patterns = [
        'i need ideas', 'fresh ideas', 'new ideas', 'creative ideas', 'stuck', 'help me think',
        # ADD THESE:
        'need fresh', 'fresh', 'ideas for', 'new approach', 'different approach',
        'inspire', 'inspiration', 'creative', 'innovative'
    ]
    
    # Perspective shift patterns (add these)
    perspective_shift_patterns = [
        'help me see this from a different angle', 'different angle', 'see this differently',
        'think about this differently', 'different perspective', 'another way to think',
        # ADD THESE:
        'perspective', 'viewpoint', 'angle', 'differently', 'another way',
        'alternative', 'fresh perspective', 'new perspective'
    ]
    ```
    """)

# Test Current Implementation
st.header("🧪 Current Implementation Test")

if st.button("🔬 Test Current Trigger Implementation"):
    
    st.markdown("**Testing the actual _should_apply_gamification method:**")
    
    for test_case in user_test_cases:
        # Create test state
        state = create_test_state([test_case['message']])
        
        # Test the actual method
        processor = st.session_state.challenge_processor
        result = processor._should_apply_gamification(state, "user_perspective", "perspective_challenge")
        
        st.markdown(f"**{test_case['name']}:** {'✅ TRIGGERS' if result else '❌ NO TRIGGER'}")
        st.text(f"  Message: \"{test_case['message']}\"")
        st.text(f"  Expected: {test_case['expected']}")
        
        if not result:
            st.error(f"❌ FAILED - Should have triggered {test_case['trigger_type']}")

st.markdown("---")
st.markdown("**🎮 Use this test to identify and fix gamification trigger issues!**")
