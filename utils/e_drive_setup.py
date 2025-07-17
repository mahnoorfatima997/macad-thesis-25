#!/usr/bin/env python3
"""
E-Drive Setup Utility
Moves all model storage and cache to E drive to save C drive space
"""

import os
import shutil
import sys
from pathlib import Path

def setup_e_drive_environment():
    """
    Set up environment variables to use E drive for all model storage and cache
    
    Returns:
        str: Path to the E drive cache directory
    """
    # Define E drive paths
    e_drive_base = "E:/macad-thesis-25"
    e_cache_dir = os.path.join(e_drive_base, "cache")
    e_models_dir = os.path.join(e_drive_base, "models")
    e_yolo_cache = os.path.join(e_cache_dir, "yolo")
    e_transformers_cache = os.path.join(e_cache_dir, "transformers")
    e_huggingface_cache = os.path.join(e_cache_dir, "huggingface")
    e_ultralytics_cache = os.path.join(e_cache_dir, "ultralytics")
    
    # Create directories if they don't exist
    directories = [
        e_cache_dir,
        e_models_dir,
        e_yolo_cache,
        e_transformers_cache,
        e_huggingface_cache,
        e_ultralytics_cache
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Created directory: {directory}")
    
    # Set environment variables for different libraries
    os.environ['TRANSFORMERS_CACHE'] = e_transformers_cache
    os.environ['HF_HOME'] = e_huggingface_cache
    os.environ['TORCH_HOME'] = e_cache_dir
    os.environ['ULTRAALYTICS_CACHE_DIR'] = e_ultralytics_cache
    
    # Set Python cache directory
    os.environ['PYTHONPYCACHEPREFIX'] = os.path.join(e_cache_dir, "python_cache")
    
    # Set pip cache directory
    os.environ['PIP_CACHE_DIR'] = os.path.join(e_cache_dir, "pip")
    
    print("✓ Environment variables set for E drive storage")
    
    return e_cache_dir

def move_existing_cache_to_e_drive():
    """
    Move existing cache from C drive to E drive
    """
    print("Moving existing cache to E drive...")
    
    # Common cache locations on Windows
    cache_locations = [
        os.path.expanduser("~/.cache"),
        os.path.expanduser("~/AppData/Local/Ultralytics"),
        os.path.expanduser("~/AppData/Roaming/Ultralytics"),
        os.path.expanduser("~/AppData/Local/huggingface"),
        os.path.expanduser("~/AppData/Roaming/huggingface"),
        os.path.expanduser("~/AppData/Local/pip"),
        os.path.expanduser("~/AppData/Roaming/pip")
    ]
    
    e_cache_dir = setup_e_drive_environment()
    
    for cache_path in cache_locations:
        if os.path.exists(cache_path):
            try:
                # Determine destination based on cache type
                if "ultralytics" in cache_path.lower():
                    dest = os.path.join(e_cache_dir, "ultralytics")
                elif "huggingface" in cache_path.lower():
                    dest = os.path.join(e_cache_dir, "huggingface")
                elif "pip" in cache_path.lower():
                    dest = os.path.join(e_cache_dir, "pip")
                else:
                    dest = os.path.join(e_cache_dir, "misc")
                
                # Create destination directory
                os.makedirs(dest, exist_ok=True)
                
                # Move files
                for item in os.listdir(cache_path):
                    src_item = os.path.join(cache_path, item)
                    dst_item = os.path.join(dest, item)
                    
                    if os.path.exists(dst_item):
                        # If destination exists, merge directories
                        if os.path.isdir(src_item) and os.path.isdir(dst_item):
                            shutil.copytree(src_item, dst_item, dirs_exist_ok=True)
                            shutil.rmtree(src_item)
                        else:
                            # Skip if file already exists
                            continue
                    else:
                        # Move to destination
                        shutil.move(src_item, dst_item)
                
                print(f"✓ Moved cache from: {cache_path}")
                
            except Exception as e:
                print(f"⚠️  Warning: Could not move {cache_path}: {e}")

def cleanup_c_drive_cache():
    """
    Clean up remaining cache on C drive
    """
    print("Cleaning up C drive cache...")
    
    # Common cache locations to clean
    cache_locations = [
        os.path.expanduser("~/.cache"),
        os.path.expanduser("~/AppData/Local/Ultralytics"),
        os.path.expanduser("~/AppData/Roaming/Ultralytics"),
        os.path.expanduser("~/AppData/Local/huggingface"),
        os.path.expanduser("~/AppData/Roaming/huggingface"),
        os.path.expanduser("~/AppData/Local/pip"),
        os.path.expanduser("~/AppData/Roaming/pip"),
        os.path.expanduser("~/AppData/Local/torch"),
        os.path.expanduser("~/AppData/Roaming/torch")
    ]
    
    for cache_path in cache_locations:
        if os.path.exists(cache_path):
            try:
                shutil.rmtree(cache_path)
                print(f"✓ Cleaned: {cache_path}")
            except Exception as e:
                print(f"⚠️  Warning: Could not clean {cache_path}: {e}")

def create_cache_cleanup_script():
    """
    Create a script to clean C drive cache
    """
    cleanup_script = """@echo off
echo Cleaning C drive cache for MACAD Thesis...
echo.

echo Cleaning Python cache...
if exist "%USERPROFILE%\\.cache" rmdir /s /q "%USERPROFILE%\\.cache"

echo Cleaning Ultralytics cache...
if exist "%LOCALAPPDATA%\\Ultralytics" rmdir /s /q "%LOCALAPPDATA%\\Ultralytics"
if exist "%APPDATA%\\Ultralytics" rmdir /s /q "%APPDATA%\\Ultralytics"

echo Cleaning HuggingFace cache...
if exist "%LOCALAPPDATA%\\huggingface" rmdir /s /q "%LOCALAPPDATA%\\huggingface"
if exist "%APPDATA%\\huggingface" rmdir /s /q "%APPDATA%\\huggingface"

echo Cleaning pip cache...
if exist "%LOCALAPPDATA%\\pip" rmdir /s /q "%LOCALAPPDATA%\\pip"
if exist "%APPDATA%\\pip" rmdir /s /q "%APPDATA%\\pip"

echo Cleaning PyTorch cache...
if exist "%LOCALAPPDATA%\\torch" rmdir /s /q "%LOCALAPPDATA%\\torch"
if exist "%APPDATA%\\torch" rmdir /s /q "%APPDATA%\\torch"

echo.
echo Cache cleanup completed!
echo All models and cache are now stored on E drive.
pause
"""
    
    with open("cleanup_c_drive_cache.bat", "w") as f:
        f.write(cleanup_script)
    
    print("✓ Created cleanup script: cleanup_c_drive_cache.bat")

def main():
    """Main setup function"""
    print("="*60)
    print("E-DRIVE SETUP FOR MACAD THESIS")
    print("="*60)
    print()
    
    # Check if E drive exists
    if not os.path.exists("E:/"):
        print("❌ Error: E drive not found!")
        print("Please ensure E drive is available and accessible.")
        return
    
    print("Setting up E drive environment...")
    e_cache_dir = setup_e_drive_environment()
    
    print("\nMoving existing cache to E drive...")
    move_existing_cache_to_e_drive()
    
    print("\nCreating cleanup script...")
    create_cache_cleanup_script()
    
    print("\n" + "="*60)
    print("SETUP COMPLETED!")
    print("="*60)
    print(f"✓ All cache directories created on E drive")
    print(f"✓ Environment variables configured")
    print(f"✓ Cleanup script created: cleanup_c_drive_cache.bat")
    print()
    print("Next steps:")
    print("1. Run: python cleanup_c_drive_cache.bat (as administrator)")
    print("2. Restart your terminal/IDE")
    print("3. Test the system with: python app.py data/sample_image.jpg")
    print()
    print("All future models and cache will be stored on E drive!")

if __name__ == "__main__":
    main() 