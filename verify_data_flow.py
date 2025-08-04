"""
Verify that real assessment data flows correctly through the entire pipeline
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
from pathlib import Path
import json

def verify_data_flow():
    """Verify the complete data flow from test dashboard to benchmarking"""
    
    print("DATA FLOW VERIFICATION")
    print("=" * 60)
    
    # Step 1: Check if test data exists with real assessment
    thesis_data_path = Path("thesis_data")
    if not thesis_data_path.exists():
        print("WARNING: No thesis_data directory found. Run test dashboard first.")
        return
    
    # Find interaction CSV files
    interaction_files = list(thesis_data_path.glob("interactions_*.csv"))
    print(f"\n1. TEST DATA CHECK:")
    print(f"   Found {len(interaction_files)} interaction files")
    
    if interaction_files:
        # Check a sample file for real assessment columns
        sample_file = interaction_files[0]
        df = pd.read_csv(sample_file)
        
        print(f"\n   Checking {sample_file.name}:")
        
        # Key columns for real assessment
        assessment_columns = [
            'prevents_cognitive_offloading',
            'encourages_deep_thinking',
            'provides_scaffolding',
            'maintains_engagement',
            'adapts_to_skill_level'
        ]
        
        for col in assessment_columns:
            if col in df.columns:
                values = df[col].values
                if len(values) > 0:
                    print(f"   [OK] {col}: Found with values {values[:3]}... (mean: {values.mean():.2f})")
                else:
                    print(f"   [OK] {col}: Found but empty")
            else:
                print(f"   [X] {col}: MISSING!")
    
    # Step 2: Check master metrics generation
    print(f"\n2. MASTER METRICS GENERATION:")
    results_path = Path("benchmarking/results")
    
    if (results_path / "master_session_metrics.csv").exists():
        master_df = pd.read_csv(results_path / "master_session_metrics.csv")
        print(f"   [OK] master_session_metrics.csv exists with {len(master_df)} sessions")
        
        # Check key columns that use real assessment
        if 'prevention_rate' in master_df.columns:
            print(f"   [OK] prevention_rate: {master_df['prevention_rate'].values[:3]}...")
        if 'deep_thinking_rate' in master_df.columns:
            print(f"   [OK] deep_thinking_rate: {master_df['deep_thinking_rate'].values[:3]}...")
        
        # Check for variance (no more hardcoded values)
        prevention_variance = master_df['prevention_rate'].std()
        thinking_variance = master_df['deep_thinking_rate'].std()
        print(f"   Prevention rate variance: {prevention_variance:.3f}")
        print(f"   Deep thinking variance: {thinking_variance:.3f}")
        
        if prevention_variance > 0.1 or thinking_variance > 0.1:
            print("   [OK] Good variance - not using hardcoded values!")
        else:
            print("   [WARNING] Low variance - might still be using hardcoded values")
    else:
        print("   [X] master_session_metrics.csv not found - run benchmarking analysis")
    
    # Step 3: Trace specific calculation
    print(f"\n3. CALCULATION TRACE:")
    print("   The flow is:")
    print("   a) Test dashboard logs interaction with real assessment")
    print("   b) generate_master_metrics.py reads 'prevents_cognitive_offloading' column")
    print("   c) Calculates prevention_rate = sum(prevents_cognitive_offloading) / count")
    print("   d) Same for deep_thinking_rate from 'encourages_deep_thinking'")
    print("   e) These feed into proficiency classification and all dashboard metrics")
    
    # Step 4: Check if we need to regenerate
    print(f"\n4. RECOMMENDATIONS:")
    if interaction_files:
        # Check if any files are newer than master metrics
        newest_interaction = max(f.stat().st_mtime for f in interaction_files)
        
        if (results_path / "master_session_metrics.csv").exists():
            master_mtime = (results_path / "master_session_metrics.csv").stat().st_mtime
            
            if newest_interaction > master_mtime:
                print("   [WARNING] New test data detected! Re-run benchmarking analysis:")
                print("     python benchmarking/run_benchmarking.py")
            else:
                print("   [OK] Master metrics are up to date")
        else:
            print("   [WARNING] No master metrics found. Run benchmarking analysis:")
            print("     python benchmarking/run_benchmarking.py")

if __name__ == "__main__":
    verify_data_flow()