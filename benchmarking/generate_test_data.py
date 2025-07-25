#!/usr/bin/env python
"""
Generate test interaction data for benchmarking system testing
This creates synthetic session data to test the benchmarking pipeline
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import uuid
import json
import os
from pathlib import Path

def generate_test_session(session_num: int, num_interactions: int = 10, skill_level: str = "intermediate"):
    """Generate a synthetic session with realistic interaction patterns"""
    
    session_id = str(uuid.uuid4())
    base_time = datetime.now() - timedelta(hours=session_num)
    
    interactions = []
    
    # Define interaction patterns based on skill level
    if skill_level == "beginner":
        offload_rate = 0.3  # More likely to seek direct answers
        thinking_rate = 0.4
        scaffolding_rate = 0.8
    elif skill_level == "intermediate":
        offload_rate = 0.6
        thinking_rate = 0.6
        scaffolding_rate = 0.6
    else:  # advanced
        offload_rate = 0.8
        thinking_rate = 0.8
        scaffolding_rate = 0.3
    
    # Question types and responses
    question_types = [
        ("Can you review my spatial organization?", "feedback_request"),
        ("What precedents exist for pavilion design?", "knowledge_seeking"),
        ("How can I improve the circulation?", "improvement_seeking"),
        ("I think my design is perfect", "overconfident_statement"),
        ("Why is natural lighting important?", "direct_question"),
        ("The layout seems efficient to me", "general_statement")
    ]
    
    routing_paths = ["socratic_focus", "knowledge_only", "cognitive_challenge", "multi_agent"]
    
    for i in range(num_interactions):
        # Select random question
        question, input_type = question_types[i % len(question_types)]
        
        # Generate response based on routing
        routing = np.random.choice(routing_paths)
        
        # Determine agents used
        if routing == "multi_agent":
            agents = ["domain_expert", "socratic_tutor", "cognitive_enhancement"]
        elif routing == "socratic_focus":
            agents = ["socratic_tutor"]
        elif routing == "knowledge_only":
            agents = ["domain_expert"]
        else:
            agents = ["cognitive_enhancement", "socratic_tutor"]
        
        # Generate metrics based on skill level and routing
        prevents_offload = np.random.random() < offload_rate
        encourages_thinking = np.random.random() < thinking_rate
        provides_scaffolding = np.random.random() < scaffolding_rate
        
        # Create interaction
        interaction = {
            "session_id": session_id,
            "timestamp": (base_time + timedelta(minutes=i*5)).isoformat(),
            "interaction_number": i + 1,
            "student_input": question,
            "input_length": len(question.split()),
            "input_type": input_type,
            "student_skill_level": skill_level,
            "understanding_level": np.random.choice(["low", "medium", "high"]),
            "confidence_level": np.random.choice(["uncertain", "confident", "overconfident"]),
            "engagement_level": np.random.choice(["low", "medium", "high"]),
            "agent_response": f"Based on your {input_type}, I'd like to explore... [sample response]",
            "response_length": np.random.randint(50, 150),
            "routing_path": routing,
            "agents_used": agents,
            "response_type": f"{routing}_response",
            "primary_agent": agents[0],
            "cognitive_flags": json.dumps(["spatial_reasoning"] if np.random.random() > 0.5 else []),
            "cognitive_flags_count": 1 if np.random.random() > 0.5 else 0,
            "confidence_score": np.random.uniform(0.4, 0.9),
            "sources_used": json.dumps(["https://example.com/architecture"] if np.random.random() > 0.5 else []),
            "knowledge_integrated": np.random.random() > 0.5,
            "sources_count": 1 if np.random.random() > 0.5 else 0,
            "response_time": np.random.uniform(0.5, 3.0),
            "prevents_cognitive_offloading": prevents_offload,
            "encourages_deep_thinking": encourages_thinking,
            "provides_scaffolding": provides_scaffolding,
            "maintains_engagement": np.random.random() > 0.3,
            "adapts_to_skill_level": np.random.random() > 0.4,
            "multi_agent_coordination": len(agents) > 1,
            "appropriate_agent_selection": np.random.random() > 0.3,
            "response_coherence": np.random.random() > 0.2,
            "metadata": json.dumps({"test_session": True})
        }
        
        interactions.append(interaction)
    
    return pd.DataFrame(interactions), session_id

def main():
    """Generate multiple test sessions"""
    
    # Create thesis_data directory if it doesn't exist
    data_dir = Path("./thesis_data")
    data_dir.mkdir(exist_ok=True)
    
    print("Generating test interaction data for benchmarking...")
    
    # Generate sessions with different characteristics
    sessions = [
        ("beginner", 15),
        ("intermediate", 20),
        ("intermediate", 12),
        ("advanced", 18),
        ("beginner", 10)
    ]
    
    generated_files = []
    
    for i, (skill_level, num_interactions) in enumerate(sessions):
        print(f"\nGenerating session {i+1} ({skill_level}, {num_interactions} interactions)...")
        
        # Generate session data
        df, session_id = generate_test_session(i, num_interactions, skill_level)
        
        # Save to CSV
        filename = f"interactions_{session_id}.csv"
        filepath = data_dir / filename
        df.to_csv(filepath, index=False)
        
        generated_files.append(filename)
        print(f"  ✅ Saved: {filename}")
        
        # Print summary
        print(f"  - Skill level: {skill_level}")
        print(f"  - Interactions: {len(df)}")
        print(f"  - Offload prevention rate: {df['prevents_cognitive_offloading'].mean():.2%}")
        print(f"  - Deep thinking rate: {df['encourages_deep_thinking'].mean():.2%}")
    
    print(f"\n✅ Generated {len(generated_files)} test sessions in ./thesis_data/")
    print("\nYou can now run the benchmarking tool:")
    print("  python benchmarking/run_benchmarking.py")
    
    # Also create a summary file
    summary = {
        "generated_at": datetime.now().isoformat(),
        "test_sessions": len(generated_files),
        "files": generated_files,
        "purpose": "Test data for benchmarking system development"
    }
    
    with open(data_dir / "test_data_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    print("\nNote: This is synthetic test data. For real analysis, use actual session data.")

if __name__ == "__main__":
    main()