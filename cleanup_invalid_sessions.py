"""
Move invalid CSV files to backup folder
Only keep CSV files with all required columns for benchmarking
"""
import pandas as pd
from pathlib import Path
import shutil
from datetime import datetime

# Required columns for the dashboard
REQUIRED_COLUMNS = [
    'prevents_cognitive_offloading',
    'encourages_deep_thinking', 
    'provides_scaffolding',
    'maintains_engagement',
    'adapts_to_skill_level',
    'multi_agent_coordination',
    'appropriate_agent_selection',
    'response_coherence',
    'knowledge_integrated',
    'sources_count'
]

def cleanup_invalid_sessions():
    data_dir = Path("thesis_data")
    backup_dir = data_dir / "outdated_csv_backup"
    
    # Create backup directory if it doesn't exist
    backup_dir.mkdir(exist_ok=True)
    
    # Get all interaction CSV files
    csv_files = list(data_dir.glob("interactions_*.csv"))
    
    valid_files = []
    invalid_files = []
    empty_files = []
    
    print("Checking CSV files for required columns...")
    print(f"Total CSV files found: {len(csv_files)}")
    
    for csv_file in csv_files:
        try:
            # Check if file is empty
            df = pd.read_csv(csv_file)
            if len(df) == 0:
                empty_files.append(csv_file)
                print(f"  [EMPTY] {csv_file.name}")
                continue
                
            # Check for required columns
            missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
            
            if missing_columns:
                invalid_files.append(csv_file)
                print(f"  [INVALID] {csv_file.name} - Missing {len(missing_columns)} columns")
            else:
                valid_files.append(csv_file)
                print(f"  [OK] {csv_file.name}")
                
        except Exception as e:
            invalid_files.append(csv_file)
            print(f"  [ERROR] {csv_file.name}: {e}")
    
    print(f"\nSummary:")
    print(f"  Valid files: {len(valid_files)}")
    print(f"  Invalid files: {len(invalid_files)}")
    print(f"  Empty files: {len(empty_files)}")
    
    # Move invalid and empty files to backup
    files_to_move = invalid_files + empty_files
    
    if files_to_move:
        print(f"\nMoving {len(files_to_move)} invalid/empty files to backup folder...")
        for file in files_to_move:
            backup_path = backup_dir / file.name
            print(f"  Moving {file.name} to backup...")
            shutil.move(str(file), str(backup_path))
        print(f"Moved {len(files_to_move)} files to {backup_dir}")
    else:
        print("\nNo files to move.")
    
    print(f"\nRemaining valid sessions: {len(valid_files)}")
    
    return valid_files, invalid_files, empty_files

def clean_master_metrics():
    """Remove entries from master metrics that correspond to invalid sessions"""
    
    # Get list of valid session IDs
    data_dir = Path("thesis_data")
    valid_sessions = []
    
    for csv_file in data_dir.glob("interactions_*.csv"):
        # Extract session ID from filename
        session_id = csv_file.stem.replace("interactions_", "")
        valid_sessions.append(session_id)
    
    print(f"\nValid session IDs: {len(valid_sessions)}")
    
    # Clean up master_session_metrics.csv in results folder
    results_metrics_file = Path("results/master_session_metrics.csv")
    if results_metrics_file.exists():
        print(f"\nCleaning {results_metrics_file}...")
        df = pd.read_csv(results_metrics_file)
        original_count = len(df)
        
        # Filter to only valid sessions
        df_clean = df[df['session_id'].isin(valid_sessions)]
        cleaned_count = len(df_clean)
        
        # Save cleaned version
        df_clean.to_csv(results_metrics_file, index=False)
        print(f"  Cleaned: {original_count} -> {cleaned_count} sessions")
    
    # Also clean the benchmarking results version
    bench_metrics_file = Path("benchmarking/results/master_session_metrics.csv")
    if bench_metrics_file.exists():
        print(f"\nCleaning {bench_metrics_file}...")
        df = pd.read_csv(bench_metrics_file)
        original_count = len(df)
        
        # Filter to only valid sessions
        df_clean = df[df['session_id'].isin(valid_sessions)]
        cleaned_count = len(df_clean)
        
        # Save cleaned version
        df_clean.to_csv(bench_metrics_file, index=False)
        print(f"  Cleaned: {original_count} -> {cleaned_count} sessions")

if __name__ == "__main__":
    print("="*60)
    print("CLEANING UP INVALID SESSION FILES")
    print("="*60)
    
    # Move invalid files
    valid, invalid, empty = cleanup_invalid_sessions()
    
    # Clean master metrics
    clean_master_metrics()
    
    print("\n" + "="*60)
    print("CLEANUP COMPLETE!")
    print("="*60)
    print(f"Valid sessions remaining: {len(valid)}")
    print("You can now run the benchmarking dashboard with consistent data.")