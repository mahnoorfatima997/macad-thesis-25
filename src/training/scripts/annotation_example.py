#!/usr/bin/env python3
"""
Architectural Annotation Example
Shows how to create YOLO annotations for architectural elements
"""

import cv2
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches

class ArchitecturalAnnotator:
    """Example of how to annotate architectural elements"""
    
    def __init__(self):
        # YOLO class mapping for architectural elements
        self.classes = {
            0: 'corridor',
            1: 'door', 
            2: 'window',
            3: 'wall',
            4: 'room',
            5: 'stairs',
            6: 'toilet',
            7: 'kitchen',
            8: 'bedroom',
            9: 'living_room',
            10: 'entrance'
        }
        
        # Colors for visualization
        self.colors = {
            'corridor': (255, 0, 0),    # Red
            'door': (0, 255, 0),        # Green
            'window': (0, 0, 255),      # Blue
            'wall': (255, 255, 0),      # Yellow
            'room': (255, 0, 255),      # Magenta
            'stairs': (0, 255, 255),    # Cyan
            'toilet': (128, 0, 128),    # Purple
            'kitchen': (255, 165, 0),   # Orange
            'bedroom': (0, 128, 0),     # Dark Green
            'living_room': (128, 0, 0), # Dark Red
            'entrance': (0, 0, 128)     # Dark Blue
        }
    
    def create_sample_annotation(self):
        """Create a sample annotation for a floor plan"""
        
        # Example: Floor plan with corridor, doors, and rooms
        annotations = [
            # Corridor (long rectangular shape in center)
            "0 0.45 0.5 0.1 0.8",      # corridor: center, 10% wide, 80% tall
            
            # Doors along the corridor
            "1 0.4 0.1 0.05 0.08",     # door 1: left side, top
            "1 0.4 0.25 0.05 0.08",    # door 2: left side, middle
            "1 0.4 0.75 0.05 0.08",    # door 3: left side, bottom
            "1 0.55 0.15 0.05 0.08",   # door 4: right side, top
            "1 0.55 0.35 0.05 0.08",   # door 5: right side, middle
            "1 0.55 0.85 0.05 0.08",   # door 6: right side, bottom
            
            # Rooms (rectangular areas)
            "4 0.1 0.1 0.3 0.3",       # room 1: top left
            "4 0.1 0.45 0.3 0.3",      # room 2: middle left
            "4 0.1 0.8 0.3 0.15",      # room 3: bottom left
            "4 0.65 0.1 0.25 0.3",     # room 4: top right
            "4 0.65 0.45 0.25 0.3",    # room 5: middle right
            "4 0.65 0.8 0.25 0.15",    # room 6: bottom right
            
            # Windows in rooms
            "2 0.15 0.15 0.1 0.05",    # window in room 1
            "2 0.15 0.5 0.1 0.05",     # window in room 2
            "2 0.7 0.15 0.1 0.05",     # window in room 4
            "2 0.7 0.5 0.1 0.05",      # window in room 5
            
            # Entrance
            "10 0.45 0.95 0.1 0.05"    # entrance: bottom center
        ]
        
        return annotations
    
    def explain_yolo_format(self):
        """Explain YOLO annotation format"""
        print("🎯 YOLO ANNOTATION FORMAT EXPLAINED")
        print("=" * 50)
        
        print("Format: <class_id> <center_x> <center_y> <width> <height>")
        print("All values are normalized (0.0 to 1.0)")
        print()
        
        # Example annotation
        annotation = "0 0.45 0.5 0.1 0.8"
        parts = annotation.split()
        
        print(f"Example: {annotation}")
        print(f"  Class ID: {parts[0]} ({self.classes[int(parts[0])]})")
        print(f"  Center X: {parts[1]} (45% from left)")
        print(f"  Center Y: {parts[2]} (50% from top)")
        print(f"  Width: {parts[3]} (10% of image width)")
        print(f"  Height: {parts[4]} (80% of image height)")
        print()
        
        print("📐 HOW TO MEASURE:")
        print("1. Open image in annotation tool (LabelImg)")
        print("2. Draw rectangle around architectural element")
        print("3. Tool automatically calculates normalized coordinates")
        print("4. Save as .txt file with same name as image")
    
    def create_visualization(self):
        """Create visual example of annotations"""
        print("🎨 CREATING VISUAL EXAMPLE")
        print("=" * 50)
        
        # Create a sample floor plan image
        img_size = 800
        img = np.ones((img_size, img_size, 3), dtype=np.uint8) * 255
        
        # Draw sample floor plan
        self._draw_sample_floor_plan(img)
        
        # Parse annotations
        annotations = self.create_sample_annotation()
        
        # Draw bounding boxes
        for annotation in annotations:
            self._draw_annotation_box(img, annotation)
        
        # Save visualization
        output_path = "annotation_example.jpg"
        cv2.imwrite(output_path, img)
        print(f"✓ Saved visualization to: {output_path}")
        
        return output_path
    
    def _draw_sample_floor_plan(self, img):
        """Draw a simple floor plan for demonstration"""
        # Draw walls (black lines)
        cv2.line(img, (100, 100), (700, 100), (0, 0, 0), 3)  # Top wall
        cv2.line(img, (100, 700), (700, 700), (0, 0, 0), 3)  # Bottom wall
        cv2.line(img, (100, 100), (100, 700), (0, 0, 0), 3)  # Left wall
        cv2.line(img, (700, 100), (700, 700), (0, 0, 0), 3)  # Right wall
        
        # Draw corridor (vertical line in center)
        cv2.line(img, (360, 100), (360, 700), (0, 0, 0), 3)  # Corridor wall
        cv2.line(img, (440, 100), (440, 700), (0, 0, 0), 3)  # Corridor wall
        
        # Draw horizontal walls
        cv2.line(img, (100, 280), (360, 280), (0, 0, 0), 3)  # Top horizontal
        cv2.line(img, (100, 460), (360, 460), (0, 0, 0), 3)  # Middle horizontal
        cv2.line(img, (100, 640), (360, 640), (0, 0, 0), 3)  # Bottom horizontal
        cv2.line(img, (440, 280), (700, 280), (0, 0, 0), 3)  # Top horizontal
        cv2.line(img, (440, 460), (700, 460), (0, 0, 0), 3)  # Middle horizontal
        cv2.line(img, (440, 640), (700, 640), (0, 0, 0), 3)  # Bottom horizontal
    
    def _draw_annotation_box(self, img, annotation):
        """Draw a bounding box from YOLO annotation"""
        parts = annotation.split()
        class_id = int(parts[0])
        center_x = float(parts[1])
        center_y = float(parts[2])
        width = float(parts[3])
        height = float(parts[4])
        
        # Convert normalized coordinates to pixel coordinates
        img_height, img_width = img.shape[:2]
        x_center = int(center_x * img_width)
        y_center = int(center_y * img_height)
        w = int(width * img_width)
        h = int(height * img_height)
        
        # Calculate top-left and bottom-right corners
        x1 = x_center - w // 2
        y1 = y_center - h // 2
        x2 = x_center + w // 2
        y2 = y_center + h // 2
        
        # Get color for this class
        class_name = self.classes[class_id]
        color = self.colors[class_name]
        
        # Draw bounding box
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
        
        # Add label
        label = f"{class_name}"
        cv2.putText(img, label, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    
    def create_training_files(self):
        """Create example training files"""
        print("📁 CREATING EXAMPLE TRAINING FILES")
        print("=" * 50)
        
        # Create directory structure
        training_dir = Path("example_training_data")
        training_dir.mkdir(exist_ok=True)
        
        (training_dir / "images" / "train").mkdir(parents=True, exist_ok=True)
        (training_dir / "images" / "val").mkdir(parents=True, exist_ok=True)
        (training_dir / "labels" / "train").mkdir(parents=True, exist_ok=True)
        (training_dir / "labels" / "val").mkdir(parents=True, exist_ok=True)
        
        # Create dataset config
        config = {
            "path": str(training_dir.absolute()),
            "train": "images/train",
            "val": "images/val",
            "nc": len(self.classes),
            "names": list(self.classes.values())
        }
        
        import yaml
        config_path = training_dir / "dataset.yaml"
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        # Create example annotation file
        annotations = self.create_sample_annotation()
        annotation_path = training_dir / "labels" / "train" / "plan_001.txt"
        with open(annotation_path, 'w') as f:
            f.write('\n'.join(annotations))
        
        print(f"✓ Created training directory: {training_dir}")
        print(f"✓ Created dataset config: {config_path}")
        print(f"✓ Created example annotation: {annotation_path}")
        
        return training_dir

def main():
    """Main function"""
    annotator = ArchitecturalAnnotator()
    
    # Explain the format
    annotator.explain_yolo_format()
    
    # Create visualization
    annotator.create_visualization()
    
    # Create training files
    training_dir = annotator.create_training_files()
    
    print(f"\n🎯 NEXT STEPS:")
    print(f"1. Copy your architectural images to: {training_dir}/images/train/")
    print(f"2. Annotate them using LabelImg or similar tool")
    print(f"3. Run the training script from quick_training_guide.md")
    print(f"4. Your model will learn to detect corridors, doors, windows, etc!")

if __name__ == "__main__":
    main() 