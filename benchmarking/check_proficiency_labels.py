#!/usr/bin/env python
"""
Quick diagnostic script to check proficiency label distribution
"""

import pandas as pd
from pathlib import Path
from user_proficiency_classifier import assign_proficiency_label

def check_label_distribution():
    """Check how proficiency labels are distributed across sessions"""
    
    data_dir = Path("./thesis_data")
    session_files = list(data_dir.glob("interactions_*.csv"))
    
    print(f"Found {len(session_files)} session files\n")
    
    labels = []
    details = []
    
    for i, session_file in enumerate(session_files):
        df = pd.read_csv(session_file)
        label = assign_proficiency_label(df)
        labels.append(label)
        
        # Calculate metrics
        offload_prev = df['prevents_cognitive_offloading'].mean()
        deep_think = df['encourages_deep_thinking'].mean()
        scaffolding = df['provides_scaffolding'].mean()
        engagement = df['maintains_engagement'].mean()
        
        details.append({
            'session': session_file.stem,
            'label': label,
            'interactions': len(df),
            'offload_prev': offload_prev,
            'deep_think': deep_think,
            'scaffolding': scaffolding,
            'engagement': engagement
        })
        
        print(f"Session {i+1}: {label}")
        print(f"  - Offload prevention: {offload_prev:.2%}")
        print(f"  - Deep thinking: {deep_think:.2%}")
        print(f"  - Scaffolding: {scaffolding:.2%}")
        print(f"  - Engagement: {engagement:.2%}")
        print()
    
    # Summary
    print("\nLabel Distribution:")
    for label in ['beginner', 'intermediate', 'advanced', 'expert']:
        count = labels.count(label)
        if count > 0:
            print(f"  {label}: {count} sessions ({count/len(labels)*100:.0f}%)")
    
    # Save detailed report
    df_report = pd.DataFrame(details)
    df_report.to_csv("./benchmarking/proficiency_label_report.csv", index=False)
    print(f"\nDetailed report saved to: ./benchmarking/proficiency_label_report.csv")
    
    return labels

if __name__ == "__main__":
    check_label_distribution()