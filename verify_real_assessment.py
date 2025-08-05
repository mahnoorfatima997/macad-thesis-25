"""
Verify that real assessment produces varied scores based on response content
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from thesis_tests.data_models import TestGroup, TestPhase, InteractionData
from thesis_tests.logging_system import TestSessionLogger
from datetime import datetime
import json
import pandas as pd

def generate_test_session_with_varied_responses():
    """Generate a test session with varied response types to verify assessment variability"""
    
    # Test responses representing different cognitive enhancement levels
    test_interactions = [
        # HIGH COGNITIVE ENHANCEMENT (Socratic, challenging)
        {
            "user": "How should I design this building?",
            "system": "That's a great question! Let's explore this together. What do you think are the key factors that should influence your design? Consider the site context, user needs, and environmental conditions. How might these shape your approach?",
            "expected": "High prevention, high deep thinking"
        },
        {
            "user": "I think my design is perfect",
            "system": "It's wonderful that you're confident! Let's examine this further. What specific aspects make you feel it's perfect? Have you considered how different users might experience the space? What assumptions are you making about their needs?",
            "expected": "High prevention (challenging overconfidence)"
        },
        
        # MEDIUM COGNITIVE ENHANCEMENT (Some guidance but also answers)
        {
            "user": "What materials should I use?",
            "system": "Let's think about material selection. First, consider your climate - you'll want materials that respond well to local conditions. For example, in hot climates, materials with high thermal mass can help. What's your local climate like?",
            "expected": "Medium prevention (partial guidance)"
        },
        {
            "user": "How do I calculate loads?",
            "system": "Structural load calculation involves several steps. Let's start with understanding the types of loads. Can you identify what kinds of loads your structure might experience? Think about permanent vs. variable loads.",
            "expected": "Medium scaffolding"
        },
        
        # LOW COGNITIVE ENHANCEMENT (Direct answers)
        {
            "user": "What's the standard ceiling height?",
            "system": "The standard ceiling height is 8-10 feet for residential and 12-14 feet for commercial spaces.",
            "expected": "Low prevention (direct answer)"
        },
        {
            "user": "Tell me the fire code requirements",
            "system": "Fire code requirements: Exit doors must open outward, maximum travel distance to exit is 250 feet, minimum corridor width is 44 inches, and you need emergency lighting.",
            "expected": "Low prevention (direct listing)"
        },
        
        # VARIED ENGAGEMENT LEVELS
        {
            "user": "I'm confused about circulation",
            "system": "I understand circulation can be complex! Let's break it down. Imagine walking through your building - what path would different users take? Start by identifying your main entry points and destinations. How might you connect them?",
            "expected": "High engagement, good scaffolding"
        },
        {
            "user": "Explain the concept",
            "system": "Circulation refers to how people move through a building.",
            "expected": "Low engagement (too brief)"
        }
    ]
    
    # Create three sessions - one for each test group
    for group in [TestGroup.MENTOR, TestGroup.GENERIC_AI, TestGroup.CONTROL]:
        print(f"\n{'='*60}")
        print(f"Testing {group.value} group with varied responses")
        print(f"{'='*60}")
        
        logger = TestSessionLogger(
            session_id=f"verify_{group.value}_varied",
            participant_id=f"test_user_{group.value}",
            test_group=group
        )
        
        # Log all interactions
        for i, test in enumerate(test_interactions):
            if group == TestGroup.CONTROL:
                # Control group gets no response
                system_response = ""
            else:
                system_response = test["system"]
            
            interaction = InteractionData(
                id=f"interaction_{i}",
                session_id=logger.session_id,
                timestamp=datetime.now(),
                phase=TestPhase.IDEATION,
                user_input=test["user"],
                system_response=system_response,
                interaction_type="test",
                response_time=1.5,
                cognitive_metrics={},
                generated_moves=[],
                error_occurred=False
            )
            
            logger.log_interaction(interaction)
        
        # Finalize session
        logger.finalize_session()
        
        # Read and analyze the results
        df = pd.read_csv(logger.interactions_file)
        
        print(f"\nCognitive Assessment Results for {group.value}:")
        print("-" * 50)
        
        # Show key metrics
        metrics = ['prevents_cognitive_offloading', 'encourages_deep_thinking', 
                  'provides_scaffolding', 'maintains_engagement', 'adapts_to_skill_level']
        
        for metric in metrics:
            values = df[metric].values
            print(f"\n{metric}:")
            print(f"  Values: {values}")
            print(f"  Mean: {values.mean():.2f}")
            print(f"  Std: {values.std():.2f}")
            print(f"  Range: {values.min():.2f} - {values.max():.2f}")
        
        # Check for variability
        total_variance = sum(df[metric].std() for metric in metrics)
        print(f"\nTotal variance across all metrics: {total_variance:.2f}")
        
        if group == TestGroup.CONTROL:
            assert all(df[metric].sum() == 0 for metric in metrics[:4]), "Control should have zero cognitive enhancement"
            print("[PASS] Control group shows no cognitive enhancement")
        else:
            assert total_variance > 0, f"{group.value} should show varied assessment scores"
            print(f"[PASS] {group.value} shows varied assessment based on response content")

if __name__ == "__main__":
    generate_test_session_with_varied_responses()
    print("\n\nAll verification tests passed! Real assessment is producing varied, content-based scores.")