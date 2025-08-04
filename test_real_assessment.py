"""
Test the real cognitive assessment integration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from thesis_tests.data_models import TestGroup, TestPhase, InteractionData
from thesis_tests.logging_system import TestSessionLogger
from datetime import datetime
import json

def test_real_assessment():
    """Test real assessment with different groups and responses"""
    
    test_cases = [
        {
            "group": TestGroup.MENTOR,
            "user_input": "What is the best way to design a facade?",
            "system_response": "That's an interesting question! Let's think about this together. What factors do you think might influence facade design? Consider the building's orientation, climate, and purpose. How might these elements shape your design decisions?",
            "expected": "High prevention and deep thinking"
        },
        {
            "group": TestGroup.MENTOR,
            "user_input": "Just tell me the answer",
            "system_response": "The answer is to use a double-skin facade with automated shading systems for optimal thermal performance.",
            "expected": "Low prevention (direct answer)"
        },
        {
            "group": TestGroup.GENERIC_AI,
            "user_input": "How do I calculate structural loads?",
            "system_response": "To calculate structural loads, you should follow these steps: 1) Calculate dead loads, 2) Calculate live loads, 3) Add wind and seismic loads, 4) Apply safety factors.",
            "expected": "Low prevention (direct steps)"
        },
        {
            "group": TestGroup.CONTROL,
            "user_input": "What about circulation patterns?",
            "system_response": "",  # Control group gets no response
            "expected": "Zero scores (no AI assistance)"
        }
    ]
    
    for i, test in enumerate(test_cases):
        print(f"\n{'='*60}")
        print(f"Test Case {i+1}: {test['group'].value} - {test['expected']}")
        print(f"{'='*60}")
        
        # Create logger
        logger = TestSessionLogger(
            session_id=f"test_{i}",
            participant_id="test_user",
            test_group=test["group"]
        )
        
        # Create interaction
        interaction = InteractionData(
            id=f"interaction_{i}",
            session_id=f"test_{i}",
            timestamp=datetime.now(),
            phase=TestPhase.IDEATION,
            user_input=test["user_input"],
            system_response=test["system_response"],
            interaction_type="test",
            response_time=1.5,
            cognitive_metrics={},
            generated_moves=[],
            error_occurred=False
        )
        
        # Log interaction (this will use real assessment)
        logger.log_interaction(interaction)
        
        # Read the logged data
        with open(logger.interactions_file, 'r') as f:
            lines = f.readlines()
            if len(lines) > 1:  # Skip header
                data = lines[-1].strip()
                # Parse the CSV line to extract cognitive scores
                import csv
                reader = csv.DictReader([lines[0].strip(), data])
                for row in reader:
                    print(f"\nUser Input: {test['user_input'][:50]}...")
                    print(f"System Response: {test['system_response'][:80]}...")
                    print(f"\nCognitive Assessment Results:")
                    print(f"  - Prevents Offloading: {float(row['prevents_cognitive_offloading']):.2f}")
                    print(f"  - Encourages Deep Thinking: {float(row['encourages_deep_thinking']):.2f}")
                    print(f"  - Provides Scaffolding: {float(row['provides_scaffolding']):.2f}")
                    print(f"  - Maintains Engagement: {float(row['maintains_engagement']):.2f}")
                    print(f"  - Adapts to Skill Level: {float(row['adapts_to_skill_level']):.2f}")
                    
                    # Verify expectations
                    prevents = float(row['prevents_cognitive_offloading'])
                    encourages = float(row['encourages_deep_thinking'])
                    
                    if test['group'] == TestGroup.CONTROL:
                        assert prevents == 0.0, "Control group should have 0 prevention"
                        assert encourages == 0.0, "Control group should have 0 deep thinking"
                        print("\n[PASS] Control group correctly shows no cognitive enhancement")
                    elif "Low prevention" in test['expected']:
                        assert prevents == 0.0, "Direct answers should not prevent offloading"
                        print("\n[PASS] Direct answer correctly shows no offloading prevention")
                    elif "High prevention" in test['expected']:
                        assert prevents == 1.0, "Socratic response should prevent offloading"
                        assert encourages == 1.0, "Socratic response should encourage thinking"
                        print("\n[PASS] Socratic response correctly shows high cognitive enhancement")

if __name__ == "__main__":
    test_real_assessment()
    print("\n\nAll tests passed! Real cognitive assessment is working correctly.")