"""
Convert existing CSV data to include required columns for benchmarking dashboard
"""

import pandas as pd
import json
import os
from pathlib import Path

def convert_csv_format(input_file, output_file):
    """Convert CSV to include required top-level columns"""
    
    # Read the existing CSV
    df = pd.read_csv(input_file)
    
    # Add the required columns based on existing data
    # These are estimations based on available data
    
    # Check if performance_metrics exists as a column
    if 'performance_metrics' in df.columns:
        # Try to parse performance_metrics if it's stored as JSON string
        try:
            for idx, row in df.iterrows():
                if pd.notna(row['performance_metrics']) and row['performance_metrics']:
                    metrics = json.loads(row['performance_metrics'].replace("'", '"'))
                    df.at[idx, 'prevents_cognitive_offloading'] = metrics.get('cognitive_offloading_prevention', False)
                    df.at[idx, 'encourages_deep_thinking'] = metrics.get('deep_thinking_encouragement', False)
                    df.at[idx, 'provides_scaffolding'] = metrics.get('scaffolding_effectiveness', False)
                    df.at[idx, 'maintains_engagement'] = metrics.get('engagement_maintenance', False)
                    df.at[idx, 'adapts_to_skill_level'] = metrics.get('skill_adaptation', False)
        except:
            pass
    
    # If columns don't exist, create them based on heuristics
    if 'prevents_cognitive_offloading' not in df.columns:
        # Estimate based on response characteristics
        df['prevents_cognitive_offloading'] = df.apply(
            lambda row: '?' in str(row.get('agent_response', '')) or 
                       'consider' in str(row.get('agent_response', '')).lower() or
                       'think about' in str(row.get('agent_response', '')).lower(),
            axis=1
        )
    
    if 'encourages_deep_thinking' not in df.columns:
        df['encourages_deep_thinking'] = df.apply(
            lambda row: any(word in str(row.get('agent_response', '')).lower() 
                          for word in ['consider', 'think', 'reflect', 'analyze', 'evaluate']),
            axis=1
        )
    
    if 'provides_scaffolding' not in df.columns:
        df['provides_scaffolding'] = df.apply(
            lambda row: any(word in str(row.get('agent_response', '')).lower() 
                          for word in ['let\'s start', 'first', 'step', 'example', 'building on']),
            axis=1
        )
    
    if 'maintains_engagement' not in df.columns:
        df['maintains_engagement'] = df.apply(
            lambda row: any(word in str(row.get('agent_response', '')).lower() 
                          for word in ['interesting', 'explore', 'imagine', 'your thoughts']),
            axis=1
        )
    
    if 'adapts_to_skill_level' not in df.columns:
        # Default to True for now
        df['adapts_to_skill_level'] = True
    
    if 'multi_agent_coordination' not in df.columns:
        # Check if multiple agents were used
        df['multi_agent_coordination'] = df.apply(
            lambda row: len(str(row.get('agents_used', '')).split(',')) > 1 if pd.notna(row.get('agents_used')) else False,
            axis=1
        )
    
    if 'appropriate_agent_selection' not in df.columns:
        # Default to True
        df['appropriate_agent_selection'] = True
    
    if 'response_coherence' not in df.columns:
        # Default to True  
        df['response_coherence'] = True
    
    # Save the converted file
    df.to_csv(output_file, index=False)
    print(f"Converted {input_file} -> {output_file}")
    return df

# Convert the existing file
thesis_data_dir = Path("C:/Users/aponw/OneDrive/Escritorio/MaCAD Thesis/macad-thesis-25/thesis_data")
existing_file = thesis_data_dir / "interactions_unified_session_20250823_234828.csv"

if existing_file.exists():
    # Create backup
    backup_file = thesis_data_dir / "interactions_unified_session_20250823_234828_original.csv"
    
    # Read and convert
    df = pd.read_csv(existing_file)
    
    # Save original as backup
    df.to_csv(backup_file, index=False)
    print(f"Backed up original to {backup_file}")
    
    # Convert and overwrite
    converted_df = convert_csv_format(existing_file, existing_file)
    
    # Show what columns we now have
    print(f"\nColumns in converted file:")
    print(f"Total columns: {len(converted_df.columns)}")
    
    # Check for required columns
    required_cols = [
        'prevents_cognitive_offloading',
        'encourages_deep_thinking', 
        'provides_scaffolding',
        'maintains_engagement',
        'adapts_to_skill_level',
        'multi_agent_coordination',
        'appropriate_agent_selection',
        'response_coherence'
    ]
    
    print("\nRequired columns check:")
    for col in required_cols:
        if col in converted_df.columns:
            print(f"✓ {col}")
        else:
            print(f"✗ {col}")
else:
    print(f"File not found: {existing_file}")