#!/usr/bin/env python3
"""
Script to clean up test and debug files from the root directory
Created during troubleshooting sessions
"""

import os
import shutil
from pathlib import Path

# List of test/debug files to remove
TEST_FILES_TO_REMOVE = [
    "fix_chromadb_issue.py",
    "fix_test_data_columns.py",
    "test_color_fix.py",
    "test_imports.py",
    "test_imports_simple.py",
    "test_linkography_generation.py",
    "test_linkography_loading.py",
    "test_mentor_init.py",
    "test_mentor_orchestrator.py",
    "test_no_cognitive_summary.py",
    "test_sankey_color_fix.py",
    "test_std_fixes.py",
    "test_system_status.py",
    "migrate_test_data.py",
    "verify_data_locations.py",
    "verify_mentor_system.py",
    "verify_metrics_update.py"
]

def cleanup_test_files():
    """Remove test and debug files from root directory"""
    
    print("Cleaning up test and debug files...")
    print("=" * 60)
    
    removed_count = 0
    not_found_count = 0
    
    for filename in TEST_FILES_TO_REMOVE:
        file_path = Path(filename)
        
        if file_path.exists():
            try:
                # Remove the file
                os.remove(file_path)
                print(f"[REMOVED] {filename}")
                removed_count += 1
            except Exception as e:
                print(f"[ERROR] Could not remove {filename}: {e}")
        else:
            print(f"[NOT FOUND] {filename}")
            not_found_count += 1
    
    print("=" * 60)
    print(f"\nSummary:")
    print(f"   - Files removed: {removed_count}")
    print(f"   - Files not found: {not_found_count}")
    print(f"   - Total processed: {len(TEST_FILES_TO_REMOVE)}")
    
    # Ask about removing this cleanup script itself
    print("\n" + "=" * 60)
    response = input("\nDo you want to remove this cleanup script as well? (y/n): ")
    
    if response.lower() == 'y':
        try:
            os.remove(__file__)
            print("Cleanup script removed!")
        except Exception as e:
            print(f"Could not remove cleanup script: {e}")
    else:
        print("Keeping cleanup script for future use")
    
    print("\nCleanup complete!")

if __name__ == "__main__":
    # Confirm before proceeding
    print("CLEANUP TEST FILES")
    print("=" * 60)
    print("\nThis script will remove the following test/debug files:")
    print()
    
    for i, filename in enumerate(TEST_FILES_TO_REMOVE, 1):
        print(f"  {i:2d}. {filename}")
    
    print("\n" + "=" * 60)
    response = input("\nAre you sure you want to remove these files? (y/n): ")
    
    if response.lower() == 'y':
        cleanup_test_files()
    else:
        print("\nCleanup cancelled by user")