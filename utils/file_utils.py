import os
import shutil
from typing import List, Optional
from pathlib import Path

def ensure_directory_exists(directory_path: str) -> None:
    """
    Ensure a directory exists, create it if it doesn't
    
    Args:
        directory_path (str): Path to the directory
    """
    Path(directory_path).mkdir(parents=True, exist_ok=True)

def get_file_extension(file_path: str) -> str:
    """
    Get the file extension from a file path
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        str: File extension (including the dot)
    """
    return Path(file_path).suffix.lower()

def is_image_file(file_path: str) -> bool:
    """
    Check if a file is an image based on its extension
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        bool: True if the file is an image
    """
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.gif'}
    return get_file_extension(file_path) in image_extensions

def list_image_files(directory_path: str, recursive: bool = False) -> List[str]:
    """
    List all image files in a directory
    
    Args:
        directory_path (str): Path to the directory
        recursive (bool): Whether to search recursively
        
    Returns:
        List[str]: List of image file paths
    """
    image_files = []
    
    if recursive:
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                if is_image_file(file_path):
                    image_files.append(file_path)
    else:
        for file in os.listdir(directory_path):
            file_path = os.path.join(directory_path, file)
            if os.path.isfile(file_path) and is_image_file(file_path):
                image_files.append(file_path)
    
    return sorted(image_files)

def create_output_filename(input_path: str, suffix: str = "", extension: str = None) -> str:
    """
    Create an output filename based on input path
    
    Args:
        input_path (str): Input file path
        suffix (str): Suffix to add before extension
        extension (str): New extension (including dot)
        
    Returns:
        str: Output filename
    """
    input_path = Path(input_path)
    
    if extension is None:
        extension = input_path.suffix
    
    stem = input_path.stem
    if suffix:
        stem = f"{stem}_{suffix}"
    
    return f"{stem}{extension}"

def copy_file_with_backup(source_path: str, destination_path: str, backup_suffix: str = "_backup") -> str:
    """
    Copy a file with automatic backup if destination exists
    
    Args:
        source_path (str): Source file path
        destination_path (str): Destination file path
        backup_suffix (str): Suffix for backup files
        
    Returns:
        str: Path to the copied file
    """
    source_path = Path(source_path)
    destination_path = Path(destination_path)
    
    # Create backup if destination exists
    if destination_path.exists():
        backup_path = destination_path.with_suffix(f"{backup_suffix}{destination_path.suffix}")
        shutil.copy2(destination_path, backup_path)
        print(f"Backup created: {backup_path}")
    
    # Copy the file
    shutil.copy2(source_path, destination_path)
    return str(destination_path)

def get_file_size_mb(file_path: str) -> float:
    """
    Get file size in megabytes
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        float: File size in MB
    """
    size_bytes = os.path.getsize(file_path)
    return size_bytes / (1024 * 1024)

def validate_file_exists(file_path: str, file_type: str = "file") -> bool:
    """
    Validate that a file exists
    
    Args:
        file_path (str): Path to the file
        file_type (str): Type of file for error message
        
    Returns:
        bool: True if file exists
        
    Raises:
        FileNotFoundError: If file doesn't exist
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"{file_type.capitalize()} not found: {file_path}")
    return True

def ensure_data_directory() -> str:
    """
    Ensure the data directory exists and return its path
    
    Returns:
        str: Path to the data directory
    """
    data_dir = "data"
    ensure_directory_exists(data_dir)
    return data_dir

def ensure_output_directory() -> str:
    """
    Ensure the output directory exists and return its path
    
    Returns:
        str: Path to the output directory
    """
    output_dir = "output"
    ensure_directory_exists(output_dir)
    return output_dir
