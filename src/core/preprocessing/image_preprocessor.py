import cv2
import numpy as np
import os
from typing import Tuple, Optional

def preprocess_image(path: str, target_size: Tuple[int, int] = (1024, 1024)) -> np.ndarray:
    """
    Preprocess an image for analysis by converting to grayscale, applying blur, and resizing
    
    Args:
        path (str): Path to the input image
        target_size (tuple): Target size for resizing (width, height)
        
    Returns:
        np.ndarray: Preprocessed image
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Image file not found: {path}")
    
    # Read image
    image = cv2.imread(path)
    if image is None:
        raise ValueError(f"Could not read image from {path}")
    
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Resize to target size
    resized = cv2.resize(blurred, target_size)
    
    return resized

def enhance_image_quality(image: np.ndarray) -> np.ndarray:
    """
    Enhance image quality for better analysis
    
    Args:
        image (np.ndarray): Input image
        
    Returns:
        np.ndarray: Enhanced image
    """
    # Apply histogram equalization to improve contrast
    enhanced = cv2.equalizeHist(image)
    
    # Apply bilateral filter to preserve edges while smoothing
    enhanced = cv2.bilateralFilter(enhanced, 9, 75, 75)
    
    return enhanced

def extract_roi(image: np.ndarray, x: int, y: int, width: int, height: int) -> np.ndarray:
    """
    Extract a region of interest from an image
    
    Args:
        image (np.ndarray): Input image
        x, y (int): Top-left corner coordinates
        width, height (int): Width and height of ROI
        
    Returns:
        np.ndarray: Extracted region of interest
    """
    return image[y:y+height, x:x+width]

def save_preprocessed_image(image: np.ndarray, output_path: str) -> None:
    """
    Save preprocessed image to file
    
    Args:
        image (np.ndarray): Image to save
        output_path (str): Output file path
    """
    cv2.imwrite(output_path, image)
    print(f"Preprocessed image saved to: {output_path}")

def preprocess_for_analysis(image_path: str, output_path: Optional[str] = None) -> np.ndarray:
    """
    Complete preprocessing pipeline for site plan analysis
    
    Args:
        image_path (str): Path to input image
        output_path (str, optional): Path to save preprocessed image
        
    Returns:
        np.ndarray: Preprocessed image ready for analysis
    """
    # Basic preprocessing
    preprocessed = preprocess_image(image_path)
    
    # Enhance quality
    enhanced = enhance_image_quality(preprocessed)
    
    # Save if output path provided
    if output_path:
        save_preprocessed_image(enhanced, output_path)
    
    return enhanced
