#!/usr/bin/env python3
"""
Dataset Augmentation Script
Creates additional training examples from existing data to improve model performance
"""

import os
import cv2
import numpy as np
from pathlib import Path
import random
import shutil
from PIL import Image, ImageEnhance, ImageFilter
import yaml

class DatasetAugmenter:
    """Augment the architectural dataset with additional training examples"""
    
    def __init__(self, augmentation_factor=5):
        """
        Initialize the augmenter
        
        Args:
            augmentation_factor (int): Number of augmented versions to create per image
        """
        self.augmentation_factor = augmentation_factor
        self.images_dir = Path("images/train")
        self.labels_dir = Path("labels/train")
        self.augmented_images_dir = Path("images/train_augmented")
        self.augmented_labels_dir = Path("labels/train_augmented")
        
        # Create augmented directories
        self.augmented_images_dir.mkdir(parents=True, exist_ok=True)
        self.augmented_labels_dir.mkdir(parents=True, exist_ok=True)
    
    def augment_image_and_labels(self, image_path: Path, label_path: Path):
        """Augment a single image and its corresponding labels"""
        print(f"🔄 Augmenting {image_path.name}")
        
        # Load image
        image = cv2.imread(str(image_path))
        if image is None:
            print(f"❌ Could not load image: {image_path}")
            return
        
        # Load labels
        labels = []
        if label_path.exists():
            with open(label_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        parts = line.split()
                        if len(parts) == 5:
                            labels.append([float(x) for x in parts])
        
        # Create augmented versions
        for i in range(self.augmentation_factor):
            # Apply random augmentations
            aug_image, aug_labels = self._apply_augmentation(image, labels)
            
            # Save augmented image
            aug_image_name = f"{image_path.stem}_aug_{i:03d}{image_path.suffix}"
            aug_image_path = self.augmented_images_dir / aug_image_name
            cv2.imwrite(str(aug_image_path), aug_image)
            
            # Save augmented labels
            aug_label_name = f"{label_path.stem}_aug_{i:03d}.txt"
            aug_label_path = self.augmented_labels_dir / aug_label_name
            
            with open(aug_label_path, 'w') as f:
                for label in aug_labels:
                    f.write(f"{int(label[0])} {label[1]:.6f} {label[2]:.6f} {label[3]:.6f} {label[4]:.6f}\n")
            
            print(f"   ✓ Created {aug_image_name}")
    
    def _apply_augmentation(self, image: np.ndarray, labels: list) -> tuple:
        """Apply random augmentation to image and labels"""
        # Get image dimensions
        h, w = image.shape[:2]
        
        # Random augmentation parameters
        angle = random.uniform(-15, 15)  # Rotation
        scale = random.uniform(0.8, 1.2)  # Scale
        brightness = random.uniform(0.7, 1.3)  # Brightness
        contrast = random.uniform(0.8, 1.2)  # Contrast
        
        # Apply rotation and scaling
        center = (w // 2, h // 2)
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, scale)
        
        # Calculate new image size
        cos = np.abs(rotation_matrix[0, 0])
        sin = np.abs(rotation_matrix[0, 1])
        new_w = int((h * sin) + (w * cos))
        new_h = int((h * cos) + (w * sin))
        
        # Adjust rotation matrix for new size
        rotation_matrix[0, 2] += (new_w / 2) - center[0]
        rotation_matrix[1, 2] += (new_h / 2) - center[1]
        
        # Apply transformation to image
        aug_image = cv2.warpAffine(image, rotation_matrix, (new_w, new_h), 
                                  borderMode=cv2.BORDER_CONSTANT, borderValue=(255, 255, 255))
        
        # Apply brightness and contrast
        aug_image = cv2.convertScaleAbs(aug_image, alpha=contrast, beta=(brightness - 1) * 100)
        
        # Transform labels
        aug_labels = []
        for label in labels:
            class_id, x_center, y_center, width, height = label
            
            # Convert normalized coordinates to pixel coordinates
            x_center_px = x_center * w
            y_center_px = y_center * h
            width_px = width * w
            height_px = height * h
            
            # Apply rotation and scaling to bounding box center using matrix multiplication
            point_homogeneous = np.array([x_center_px, y_center_px, 1])
            transformed_point = rotation_matrix @ point_homogeneous
            
            # Scale the bounding box dimensions
            new_width_px = width_px * scale
            new_height_px = height_px * scale
            
            # Convert back to normalized coordinates
            new_x_center = transformed_point[0] / new_w
            new_y_center = transformed_point[1] / new_h
            new_width = new_width_px / new_w
            new_height = new_height_px / new_h
            
            # Ensure coordinates are within bounds
            new_x_center = np.clip(new_x_center, 0, 1)
            new_y_center = np.clip(new_y_center, 0, 1)
            new_width = np.clip(new_width, 0, 1)
            new_height = np.clip(new_height, 0, 1)
            
            # Only keep labels that are still valid (not too small)
            if new_width > 0.01 and new_height > 0.01:
                aug_labels.append([class_id, new_x_center, new_y_center, new_width, new_height])
        
        return aug_image, aug_labels
    
    def create_augmented_dataset(self):
        """Create augmented dataset from existing images"""
        print("🚀 CREATING AUGMENTED DATASET")
        print("=" * 50)
        
        # Get all image files
        image_files = list(self.images_dir.glob("*.jpg")) + list(self.images_dir.glob("*.png"))
        
        if not image_files:
            print("❌ No images found for augmentation")
            return False
        
        print(f"📊 Found {len(image_files)} images")
        print(f"🎯 Will create {len(image_files) * self.augmentation_factor} augmented images")
        
        # Copy original images and labels
        print("\n📋 Copying original images...")
        for image_path in image_files:
            # Copy image
            shutil.copy2(image_path, self.augmented_images_dir / image_path.name)
            
            # Copy label if exists
            label_path = self.labels_dir / f"{image_path.stem}.txt"
            if label_path.exists():
                shutil.copy2(label_path, self.augmented_labels_dir / label_path.name)
        
        # Create augmented versions
        print("\n🔄 Creating augmented versions...")
        for image_path in image_files:
            label_path = self.labels_dir / f"{image_path.stem}.txt"
            self.augment_image_and_labels(image_path, label_path)
        
        # Update dataset.yaml
        self._update_dataset_yaml()
        
        print(f"\n✅ Augmentation complete!")
        print(f"📁 Original images: {len(image_files)}")
        print(f"📁 Augmented images: {len(image_files) * (self.augmentation_factor + 1)}")
        print(f"📁 Total images: {len(image_files) * (self.augmentation_factor + 1)}")
        
        return True
    
    def _update_dataset_yaml(self):
        """Update dataset.yaml to use augmented dataset"""
        yaml_path = Path("dataset.yaml")
        
        if yaml_path.exists():
            with open(yaml_path, 'r') as f:
                config = yaml.safe_load(f)
            
            # Update paths to use augmented dataset
            config['train'] = 'images/train_augmented'
            config['val'] = 'images/train_augmented'  # Use same for validation initially
            
            # Save updated config
            with open(yaml_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
            
            print("✅ Updated dataset.yaml to use augmented dataset")

def main():
    """Main function"""
    print("🎯 ARCHITECTURAL DATASET AUGMENTATION")
    print("=" * 50)
    
    # Initialize augmenter
    augmenter = DatasetAugmenter(augmentation_factor=5)
    
    # Create augmented dataset
    success = augmenter.create_augmented_dataset()
    
    if success:
        print("\n🎉 Dataset augmentation completed successfully!")
        print("🚀 You can now retrain your model with the augmented dataset.")
    else:
        print("\n❌ Dataset augmentation failed!")

if __name__ == "__main__":
    main() 