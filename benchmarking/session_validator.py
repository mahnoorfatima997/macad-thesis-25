"""Session validation utility to ensure consistent session counts across dashboard"""
import pandas as pd
from pathlib import Path
from typing import List, Tuple

# Required columns for cognitive benchmarking
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

def get_valid_session_files(data_dir: Path = None) -> List[Path]:
    """
    Returns only session files that have all required columns.
    This ensures consistent session counts across all dashboard sections.
    """
    if data_dir is None:
        data_dir = Path("thesis_data")
    
    session_files = list(data_dir.glob("interactions_*.csv"))
    valid_files = []
    
    for file in session_files:
        try:
            # Read just the header to check columns
            df = pd.read_csv(file, nrows=0)
            
            # Check if all required columns are present
            missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
            
            if not missing_columns:
                valid_files.append(file)
                
        except Exception:
            # Skip files that can't be read
            continue
    
    return valid_files

def validate_dataframe(df: pd.DataFrame) -> bool:
    """Check if a dataframe has all required columns"""
    missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    return len(missing_columns) == 0

def filter_valid_sessions(session_files: List[Path]) -> Tuple[List[Path], List[Path]]:
    """
    Filter session files into valid and invalid lists.
    Returns (valid_files, invalid_files)
    """
    valid_files = []
    invalid_files = []
    
    for file in session_files:
        try:
            df = pd.read_csv(file, nrows=0)
            if validate_dataframe(df):
                valid_files.append(file)
            else:
                invalid_files.append(file)
        except Exception:
            invalid_files.append(file)
    
    return valid_files, invalid_files