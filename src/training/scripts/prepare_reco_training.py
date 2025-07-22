#!/usr/bin/env python3
"""
ReCo Dataset Preparation for Training
Extract and prepare the ReCo architectural dataset for YOLO training
"""

import json
import os
from pathlib import Path
import numpy as np
import cv2
from tqdm import tqdm
import yaml
from typing import Dict, List, Any, Tuple

class ReCoDatasetPreparator:
    """Prepare ReCo dataset for architectural training"""
    
    def __init__(self, reco_path: str = "data/datasets/ReCo_geojson.json", output_dir: str = "datasets/reco_training"):
        self.reco_path = Path(reco_path)
        self.output_dir = Path(output_dir)
        self.images_dir = self.output_dir / "images"
        self.labels_dir = self.output_dir / "labels"
        
        # Create directory structure
        for split in ["train", "val", "test"]:
            (self.images_dir / split).mkdir(parents=True, exist_ok=True)
            (self.labels_dir / split).mkdir(parents=True, exist_ok=True)
        
        # Architectural classes based on ReCo dataset
        self.classes = [
            "room", "door", "window", "wall", "corridor", 
            "kitchen", "bathroom", "bedroom", "living_room", "entrance"
        ]
        
        # Class mapping from ReCo to our classes
        self.class_mapping = {
            "room": 0,
            "door": 1, 
            "window": 2,
            "wall": 3,
            "corridor": 4,
            "kitchen": 5,
            "bathroom": 6,
            "bedroom": 7,
            "living_room": 8,
            "entrance": 9
        }
    
    def analyze_reco_structure(self):
        """Analyze the structure of the ReCo dataset"""
        print("🔍 ANALYZING RECO DATASET STRUCTURE")
        print("=" * 50)
        
        if not self.reco_path.exists():
            print(f"❌ ReCo dataset not found at {self.reco_path}")
            return False
        
        print(f"📁 Dataset size: {self.reco_path.stat().st_size / (1024**3):.2f} GB")
        
        # Read first part to understand structure
        with open(self.reco_path, 'r', encoding='utf-8') as f:
            # Read first 2000 characters to get a complete feature
            sample = f.read(2000)
            
            # Find the first complete feature
            start_idx = sample.find('"features"')
            if start_idx != -1:
                feature_start = sample.find('[', start_idx)
                if feature_start != -1:
                    # Try to find the end of first feature
                    brace_count = 0
                    feature_end = feature_start
                    for i in range(feature_start, len(sample)):
                        if sample[i] == '{':
                            brace_count += 1
                        elif sample[i] == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                feature_end = i + 1
                                break
                    
                    if feature_end > feature_start:
                        feature_sample = sample[feature_start:feature_end]
                        print(f"\n📋 Sample feature structure:")
                        print(feature_sample[:500] + "...")
        
        return True
    
    def extract_reco_features(self, max_features: int = 1000):
        """Extract features from ReCo dataset"""
        print(f"\n📥 EXTRACTING RECO FEATURES")
        print("=" * 50)
        
        features = []
        feature_count = 0
        
        with open(self.reco_path, 'r', encoding='utf-8') as f:
            # Skip to features array
            line = f.readline()
            while line and '"features"' not in line:
                line = f.readline()
            
            if '"features"' not in line:
                print("❌ Could not find features array in ReCo dataset")
                return []
            
            # Read features
            print("📖 Reading features...")
            for line in tqdm(f, desc="Extracting features"):
                if feature_count >= max_features:
                    break
                
                if '"type": "Feature"' in line:
                    # Start of a feature
                    feature_lines = [line]
                    brace_count = line.count('{') - line.count('}')
                    
                    # Read until feature is complete
                    while brace_count > 0:
                        line = f.readline()
                        if not line:
                            break
                        feature_lines.append(line)
                        brace_count += line.count('{') - line.count('}')
                    
                    if brace_count == 0:
                        feature_json = ''.join(feature_lines)
                        try:
                            feature = json.loads(feature_json)
                            features.append(feature)
                            feature_count += 1
                        except json.JSONDecodeError:
                            continue
        
        print(f"✓ Extracted {len(features)} features")
        return features
    
    def convert_geojson_to_yolo(self, features: List[Dict[str, Any]]):
        """Convert GeoJSON features to YOLO format"""
        print(f"\n🔄 CONVERTING TO YOLO FORMAT")
        print("=" * 50)
        
        yolo_data = []
        
        for i, feature in enumerate(tqdm(features, desc="Converting features")):
            try:
                # Extract geometry and properties
                geometry = feature.get("geometry", {})
                properties = feature.get("properties", {})
                
                if geometry.get("type") != "Polygon":
                    continue
                
                # Get coordinates
                coordinates = geometry.get("coordinates", [])
                if not coordinates:
                    continue
                
                # Get room type from properties
                room_type = properties.get("room_type", "room").lower()
                class_id = self.class_mapping.get(room_type, 0)  # Default to room
                
                # Convert polygon to bounding box
                polygon = coordinates[0]  # First ring (exterior)
                if len(polygon) < 3:
                    continue
                
                # Calculate bounding box
                x_coords = [coord[0] for coord in polygon]
                y_coords = [coord[1] for coord in polygon]
                
                x_min, x_max = min(x_coords), max(x_coords)
                y_min, y_max = min(y_coords), max(y_coords)
                
                # Normalize coordinates (assuming image size 640x640)
                img_width, img_height = 640, 640
                
                # Scale coordinates to fit in image
                x_range = max(x_coords) - min(x_coords)
                y_range = max(y_coords) - min(y_coords)
                
                if x_range == 0 or y_range == 0:
                    continue
                
                # Calculate center and dimensions
                center_x = (x_min + x_max) / 2
                center_y = (y_min + y_max) / 2
                width = x_max - x_min
                height = y_max - y_min
                
                # Normalize to 0-1 range
                center_x_norm = center_x / img_width
                center_y_norm = center_y / img_height
                width_norm = width / img_width
                height_norm = height / img_height
                
                # Ensure coordinates are within bounds
                if (0 <= center_x_norm <= 1 and 0 <= center_y_norm <= 1 and 
                    0 < width_norm <= 1 and 0 < height_norm <= 1):
                    
                    yolo_data.append({
                        "id": i,
                        "class_id": class_id,
                        "class_name": room_type,
                        "center_x": center_x_norm,
                        "center_y": center_y_norm,
                        "width": width_norm,
                        "height": height_norm,
                        "properties": properties
                    })
            
            except Exception as e:
                print(f"⚠️ Error processing feature {i}: {e}")
                continue
        
        print(f"✓ Converted {len(yolo_data)} features to YOLO format")
        return yolo_data
    
    def create_synthetic_images(self, yolo_data: List[Dict[str, Any]], num_images: int = 100):
        """Create synthetic architectural images from YOLO data"""
        print(f"\n🎨 CREATING SYNTHETIC ARCHITECTURAL IMAGES")
        print("=" * 50)
        
        # Group data by similar layouts
        layout_groups = self._group_by_layout(yolo_data)
        
        images_created = 0
        
        for group_idx, group_data in enumerate(layout_groups):
            if images_created >= num_images:
                break
            
            # Create multiple images from this layout group
            images_per_group = min(5, num_images - images_created)
            
            for img_idx in range(images_per_group):
                if images_created >= num_images:
                    break
                
                # Create synthetic image
                img, labels = self._create_synthetic_layout(group_data, img_idx)
                
                # Determine split
                if images_created < int(num_images * 0.8):
                    split = "train"
                elif images_created < int(num_images * 0.9):
                    split = "val"
                else:
                    split = "test"
                
                # Save image
                img_path = self.images_dir / split / f"reco_synthetic_{images_created:04d}.jpg"
                cv2.imwrite(str(img_path), img)
                
                # Save labels
                label_path = self.labels_dir / split / f"reco_synthetic_{images_created:04d}.txt"
                with open(label_path, 'w') as f:
                    for label in labels:
                        f.write(f"{label['class_id']} {label['center_x']:.6f} {label['center_y']:.6f} {label['width']:.6f} {label['height']:.6f}\n")
                
                images_created += 1
        
        print(f"✓ Created {images_created} synthetic images")
        return images_created
    
    def _group_by_layout(self, yolo_data: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """Group YOLO data by similar layouts"""
        # Simple grouping by number of elements
        groups = {}
        
        for item in yolo_data:
            num_elements = len([d for d in yolo_data if abs(d['center_x'] - item['center_x']) < 0.1 and 
                              abs(d['center_y'] - item['center_y']) < 0.1])
            
            if num_elements not in groups:
                groups[num_elements] = []
            groups[num_elements].append(item)
        
        return list(groups.values())
    
    def _create_synthetic_layout(self, group_data: List[Dict[str, Any]], variation: int) -> Tuple[np.ndarray, List[Dict[str, Any]]]:
        """Create a synthetic architectural layout"""
        img_size = 640
        img = np.ones((img_size, img_size, 3), dtype=np.uint8) * 255
        
        labels = []
        
        # Add variation to layout
        offset_x = (variation % 3 - 1) * 0.1
        offset_y = (variation // 3 - 1) * 0.1
        
        for item in group_data:
            # Apply variation
            center_x = max(0.05, min(0.95, item['center_x'] + offset_x))
            center_y = max(0.05, min(0.95, item['center_y'] + offset_y))
            
            # Convert to pixel coordinates
            px_x = int(center_x * img_size)
            px_y = int(center_y * img_size)
            px_w = int(item['width'] * img_size)
            px_h = int(item['height'] * img_size)
            
            # Draw room
            color = self._get_room_color(item['class_name'])
            cv2.rectangle(img, (px_x - px_w//2, px_y - px_h//2), 
                         (px_x + px_w//2, px_y + px_h//2), color, -1)
            cv2.rectangle(img, (px_x - px_w//2, px_y - px_h//2), 
                         (px_x + px_w//2, px_y + px_h//2), (0, 0, 0), 2)
            
            # Add label
            labels.append({
                'class_id': item['class_id'],
                'center_x': center_x,
                'center_y': center_y,
                'width': item['width'],
                'height': item['height']
            })
        
        return img, labels
    
    def _get_room_color(self, room_type: str) -> Tuple[int, int, int]:
        """Get color for room type"""
        colors = {
            'room': (200, 200, 200),
            'kitchen': (255, 200, 200),
            'bathroom': (200, 200, 255),
            'bedroom': (200, 255, 200),
            'living_room': (255, 255, 200),
            'corridor': (150, 150, 150),
            'entrance': (255, 150, 150)
        }
        return colors.get(room_type, (200, 200, 200))
    
    def create_yolo_config(self):
        """Create YOLO configuration file"""
        print(f"\n⚙️ CREATING YOLO CONFIGURATION")
        print("=" * 50)
        
        config = {
            "path": str(self.output_dir),
            "train": "images/train",
            "val": "images/val",
            "test": "images/test",
            "nc": len(self.classes),
            "names": self.classes
        }
        
        config_path = self.output_dir / "reco_dataset.yaml"
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        print(f"✓ YOLO config saved to: {config_path}")
        return config_path
    
    def prepare_dataset(self, max_features: int = 1000, num_images: int = 100):
        """Complete dataset preparation"""
        print("🎯 PREPARING RECO DATASET FOR TRAINING")
        print("=" * 60)
        
        # Step 1: Analyze structure
        if not self.analyze_reco_structure():
            return False
        
        # Step 2: Extract features
        features = self.extract_reco_features(max_features)
        if not features:
            return False
        
        # Step 3: Convert to YOLO format
        yolo_data = self.convert_geojson_to_yolo(features)
        if not yolo_data:
            return False
        
        # Step 4: Create synthetic images
        images_created = self.create_synthetic_images(yolo_data, num_images)
        
        # Step 5: Create YOLO config
        self.create_yolo_config()
        
        print(f"\n🎉 DATASET PREPARATION COMPLETE!")
        print("=" * 60)
        print(f"📁 Dataset location: {self.output_dir}")
        print(f"📊 Features extracted: {len(features)}")
        print(f"🔄 YOLO conversions: {len(yolo_data)}")
        print(f"🎨 Synthetic images: {images_created}")
        print(f"📋 Classes: {', '.join(self.classes)}")
        
        return True

def main():
    """Main function"""
    preparator = ReCoDatasetPreparator()
    preparator.prepare_dataset(max_features=500, num_images=50)

if __name__ == "__main__":
    main() 