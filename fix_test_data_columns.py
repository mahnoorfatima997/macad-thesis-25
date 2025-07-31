"""
Fix existing test data files to include all required columns for benchmarking
"""

import pandas as pd
import json
from pathlib import Path

def fix_test_data_columns():
    """Add missing columns to test data files"""
    print("Fixing Test Data Columns for Benchmarking Compatibility")
    print("=" * 60)
    
    # Directory containing interaction files
    data_dir = Path("thesis_data")
    
    # Expected columns based on original files
    expected_columns = [
        'session_id', 'timestamp', 'interaction_number', 'student_input', 'input_length',
        'input_type', 'student_skill_level', 'understanding_level', 'confidence_level',
        'engagement_level', 'agent_response', 'response_length', 'routing_path',
        'agents_used', 'response_type', 'primary_agent', 'cognitive_flags',
        'cognitive_flags_count', 'confidence_score', 'sources_used', 'knowledge_integrated',
        'sources_count', 'response_time', 'prevents_cognitive_offloading',
        'encourages_deep_thinking', 'provides_scaffolding', 'maintains_engagement',
        'adapts_to_skill_level', 'multi_agent_coordination', 'appropriate_agent_selection',
        'response_coherence', 'metadata'
    ]
    
    # Find interaction files that might need fixing
    interaction_files = list(data_dir.glob("interactions_*.csv"))
    
    fixed_count = 0
    for file_path in interaction_files:
        try:
            # Read the CSV
            df = pd.read_csv(file_path)
            
            # Check if it's missing the expected columns
            missing_columns = set(expected_columns) - set(df.columns)
            
            if missing_columns:
                print(f"\nFixing {file_path.name}")
                print(f"  Missing columns: {len(missing_columns)}")
                
                # Add missing columns with appropriate default values
                for col in missing_columns:
                    if col == 'interaction_number':
                        df[col] = range(1, len(df) + 1)
                    elif col == 'input_length':
                        df[col] = df['user_input'].str.split().str.len() if 'user_input' in df else 10
                    elif col == 'input_type':
                        df[col] = 'general_statement'
                    elif col == 'student_skill_level':
                        df[col] = 'intermediate'
                    elif col == 'understanding_level':
                        df[col] = 'medium'
                    elif col == 'confidence_level':
                        df[col] = 'medium'
                    elif col == 'engagement_level':
                        df[col] = 'medium'
                    elif col == 'response_length':
                        df[col] = df['system_response'].str.split().str.len() if 'system_response' in df else 50
                    elif col == 'routing_path':
                        df[col] = 'test_environment'
                    elif col == 'agents_used':
                        df[col] = 'generic_ai'  # Default to generic AI
                    elif col == 'response_type':
                        df[col] = df['interaction_type'] if 'interaction_type' in df else 'general'
                    elif col == 'primary_agent':
                        df[col] = 'generic_ai'
                    elif col == 'cognitive_flags':
                        df[col] = ''
                    elif col == 'cognitive_flags_count':
                        df[col] = 0
                    elif col == 'confidence_score':
                        df[col] = 0.8
                    elif col == 'sources_used':
                        df[col] = ''
                    elif col == 'knowledge_integrated':
                        df[col] = 1
                    elif col == 'sources_count':
                        df[col] = 0
                    elif col == 'prevents_cognitive_offloading':
                        df[col] = 0.5  # Neutral default
                    elif col == 'encourages_deep_thinking':
                        df[col] = 0.5
                    elif col == 'provides_scaffolding':
                        df[col] = 0.5
                    elif col == 'maintains_engagement':
                        df[col] = 0.5
                    elif col == 'adapts_to_skill_level':
                        df[col] = 0.5
                    elif col == 'multi_agent_coordination':
                        df[col] = 0
                    elif col == 'appropriate_agent_selection':
                        df[col] = 1
                    elif col == 'response_coherence':
                        df[col] = 1
                    elif col == 'metadata':
                        # Create metadata from existing columns
                        metadata_list = []
                        for _, row in df.iterrows():
                            metadata = {
                                'phase': row.get('phase', 'unknown'),
                                'cognitive_metrics': json.loads(row.get('cognitive_metrics', '{}')) if 'cognitive_metrics' in row else {},
                                'test_group': 'generic_ai'
                            }
                            metadata_list.append(json.dumps(metadata))
                        df[col] = metadata_list
                    else:
                        df[col] = ''  # Default empty string
                
                # Rename columns if needed
                if 'user_input' in df.columns and 'student_input' not in df.columns:
                    df.rename(columns={'user_input': 'student_input'}, inplace=True)
                if 'system_response' in df.columns and 'agent_response' not in df.columns:
                    df.rename(columns={'system_response': 'agent_response'}, inplace=True)
                
                # Reorder columns to match expected order
                df = df.reindex(columns=expected_columns, fill_value='')
                
                # Save the fixed file
                df.to_csv(file_path, index=False)
                print(f"  [OK] Fixed and saved")
                fixed_count += 1
            else:
                print(f"\n{file_path.name} - Already has all columns")
                
        except Exception as e:
            print(f"\n[ERROR] Failed to fix {file_path.name}: {e}")
    
    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"- Total files processed: {len(interaction_files)}")
    print(f"- Files fixed: {fixed_count}")
    print(f"\nYour test data is now compatible with the benchmarking tools!")
    
    return fixed_count

if __name__ == "__main__":
    fix_test_data_columns()