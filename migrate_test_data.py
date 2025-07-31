"""
Migrate test data from thesis_tests directories to thesis_data for benchmarking compatibility
"""

import os
import shutil
from pathlib import Path

def migrate_test_data():
    """Migrate test data to the expected location for benchmarking tools"""
    print("Migrating Test Data for Benchmarking Compatibility")
    print("=" * 60)
    
    # Source directories
    test_data_dir = Path("thesis_tests/test_data")
    linkography_data_dir = Path("thesis_tests/linkography_data")
    
    # Target directory
    target_dir = Path("thesis_data")
    target_linkography_dir = target_dir / "linkography"
    
    # Create target directories
    target_dir.mkdir(exist_ok=True)
    target_linkography_dir.mkdir(exist_ok=True)
    
    migrated_files = []
    
    # Migrate main test data files
    if test_data_dir.exists():
        print(f"\nMigrating files from {test_data_dir} to {target_dir}")
        for file in test_data_dir.glob("*"):
            if file.is_file():
                target_path = target_dir / file.name
                try:
                    shutil.copy2(file, target_path)
                    migrated_files.append((file, target_path))
                    print(f"  [OK] {file.name}")
                except Exception as e:
                    print(f"  [FAIL] {file.name}: {e}")
    else:
        print(f"\nNo test data directory found at {test_data_dir}")
    
    # Migrate linkography data files
    if linkography_data_dir.exists():
        print(f"\nMigrating linkography files from {linkography_data_dir} to {target_linkography_dir}")
        for file in linkography_data_dir.glob("*"):
            if file.is_file():
                target_path = target_linkography_dir / file.name
                try:
                    shutil.copy2(file, target_path)
                    migrated_files.append((file, target_path))
                    print(f"  [OK] {file.name}")
                except Exception as e:
                    print(f"  [FAIL] {file.name}: {e}")
    else:
        print(f"\nNo linkography data directory found at {linkography_data_dir}")
    
    # Summary
    print(f"\n{'='*60}")
    print(f"Migration Summary:")
    print(f"- Total files migrated: {len(migrated_files)}")
    print(f"- Target directory: {target_dir}")
    print(f"- Linkography subdirectory: {target_linkography_dir}")
    
    # Check for existing data
    existing_sessions = list(target_dir.glob("interactions_*.csv"))
    print(f"\nTotal sessions in thesis_data: {len(existing_sessions)}")
    
    if migrated_files:
        print("\nMigrated files:")
        for src, dst in migrated_files[-5:]:  # Show last 5
            print(f"  {src.name} → {dst}")
        if len(migrated_files) > 5:
            print(f"  ... and {len(migrated_files) - 5} more files")
    
    print("\n[COMPLETE] Migration complete! Your test data is now available for benchmarking.")
    print("\nNext steps:")
    print("1. Run benchmarking: python benchmarking/run_benchmarking.py")
    print("2. View dashboard: python benchmarking/launch_dashboard.py")
    
    return migrated_files

if __name__ == "__main__":
    migrate_test_data()