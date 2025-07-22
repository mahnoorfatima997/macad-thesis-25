#!/usr/bin/env python3
"""
Improved Architectural Training System
Uses larger models and better training strategies for improved performance
"""

import os
import yaml
import torch
import numpy as np
from pathlib import Path
from ultralytics import YOLO
from PIL import Image
import requests
from transformers import CLIPProcessor, CLIPModel, BlipProcessor, BlipForConditionalGeneration
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Set up CUDA environment for proper GPU detection
os.environ['CUDA_VISIBLE_DEVICES'] = '0'
torch.backends.cudnn.benchmark = True

class ImprovedArchitecturalTrainer:
    """Improved trainer with better model architecture and training strategies"""
    
    def __init__(self):
        # Ensure CUDA is properly detected
        if torch.cuda.is_available():
            self.device = torch.device('cuda:0')
            print(f"🔧 Using CUDA device: {self.device}")
            print(f"   CUDA device count: {torch.cuda.device_count()}")
            print(f"   CUDA device name: {torch.cuda.get_device_name(0)}")
        else:
            self.device = torch.device('cpu')
            print(f"🔧 Using CPU device: {self.device}")
        
        # Initialize models
        self.yolo_model = None
        self.clip_model = None
        self.clip_processor = None
        self.blip_model = None
        self.blip_processor = None
        
        # Load class definitions
        self.class_names = self.load_class_names()
        
    def load_class_names(self):
        """Load class names from dataset.yaml"""
        try:
            with open("dataset.yaml", 'r') as f:
                dataset_config = yaml.safe_load(f)
            
            # Ensure we have the correct number of classes
            class_names = dataset_config.get('names', [])
            nc = dataset_config.get('nc', 103)
            
            # Validate class names
            if len(class_names) != nc:
                print(f"⚠️ Warning: Expected {nc} classes but got {len(class_names)}")
                # Pad with default names if needed
                while len(class_names) < nc:
                    class_names.append(f"class_{len(class_names)}")
            
            print(f"✅ Loaded {len(class_names)} class names")
            print(f"   Sample classes: {class_names[:10]}")
            
            return class_names
            
        except Exception as e:
            print(f"⚠️ Could not load class names: {e}")
            # Fallback to default architectural classes
            default_classes = [
                'wall', 'courtyard', 'bedroom', 'bathroom', 'door', 'living_room', 
                'dining_room', 'kitchen', 'toilet', 'corridor', 'circulation_node', 'window',
                'facade', 'roof', 'column', 'balcony', 'parapet', 'railing', 'staircase', 
                'ground_line', 'elevation_marker', 'arrow', 'text_label', 'axis', 'tree', 
                'human_figure', 'sun_path', 'shading_device', 'material_texture', 'dashed_line', 'north_arrow'
            ]
            # Pad to 103 classes
            while len(default_classes) < 103:
                default_classes.append(f"reserved_{len(default_classes)}")
            
            print(f"✅ Using default class names: {len(default_classes)} classes")
            return default_classes
    
    def load_clip_model(self):
        """Load CLIP model for semantic understanding"""
        print("🔍 Loading CLIP model...")
        try:
            self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
            self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
            self.clip_model.to(self.device)
            print("✅ CLIP model loaded successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to load CLIP: {e}")
            return False
    
    def load_blip_model(self):
        """Load BLIP model for image captioning"""
        print("📝 Loading BLIP model...")
        try:
            self.blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
            self.blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
            self.blip_model.to(self.device)
            print("✅ BLIP model loaded successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to load BLIP: {e}")
            return False
    
    def train_improved_yolo_model(self):
        """Train improved YOLO model with better architecture and strategies"""
        print("\n🚀 TRAINING IMPROVED YOLOv8 ARCHITECTURAL MODEL")
        print("=" * 60)
        
        # Check dataset
        train_images_dir = Path("images/train_augmented")  # Use augmented dataset
        if not train_images_dir.exists():
            train_images_dir = Path("images/train")  # Fallback to original
        
        train_labels_dir = Path("labels/train_augmented")  # Use augmented dataset
        if not train_labels_dir.exists():
            train_labels_dir = Path("labels/train")  # Fallback to original
        
        if not train_images_dir.exists() or not train_labels_dir.exists():
            print("❌ Training directories not found!")
            return False
        
        image_files = list(train_images_dir.glob("*.jpg")) + list(train_images_dir.glob("*.png"))
        label_files = list(train_labels_dir.glob("*.txt"))
        
        print(f"📊 Dataset Statistics:")
        print(f"   Images found: {len(image_files)}")
        print(f"   Labels found: {len(label_files)}")
        print(f"   Classes supported: {len(self.class_names)}")
        
        if len(image_files) == 0:
            print("❌ No training images found!")
            return False
        
        # Use larger model for better performance
        print("🔁 Loading larger YOLO model...")
        try:
            # Try to load YOLOv8m (medium) for better performance
            self.yolo_model = YOLO('yolov8m.pt')
            print("✅ Loaded YOLOv8m model")
        except:
            try:
                # Fallback to YOLOv8s (small)
                self.yolo_model = YOLO('yolov8s.pt')
                print("✅ Loaded YOLOv8s model")
            except:
                # Final fallback to YOLOv8n (nano)
                self.yolo_model = YOLO('yolov8n.pt')
                print("✅ Loaded YOLOv8n model")
        
        # Improved training configuration
        config = {
            'data': 'dataset.yaml',
            'epochs': 300,              # More epochs for better learning
            'imgsz': 640,
            'batch': 4,                 # Increased batch size for larger model
            'name': 'improved_architectural_yolo',
            'device': '0',              # Explicitly use GPU 0
            'workers': 2,               # Increased workers
            'patience': 100,            # Much more patience for small dataset
            'save': True,
            'save_period': 25,          # Save every 25 epochs
            'cache': False,
            'lr0': 0.0005,             # Lower learning rate for stability
            'lrf': 0.01,
            'momentum': 0.937,
            'weight_decay': 0.0005,
            'warmup_epochs': 10.0,      # More warmup epochs
            'box': 7.5,
            'cls': 0.5,
            'dfl': 1.5,
            'val': True,
            'plots': True,
            'augment': True,            # Enable augmentation
            'mixup': 0.1,               # Add mixup augmentation
            'mosaic': 1.0,              # Enable mosaic augmentation
            'degrees': 10.0,            # Rotation augmentation
            'translate': 0.1,           # Translation augmentation
            'scale': 0.5,               # Scale augmentation
            'shear': 2.0,               # Shear augmentation
            'perspective': 0.0001,      # Perspective augmentation
            'flipud': 0.0,              # No vertical flip for architectural drawings
            'fliplr': 0.5,              # Horizontal flip
            'hsv_h': 0.015,             # HSV hue augmentation
            'hsv_s': 0.7,               # HSV saturation augmentation
            'hsv_v': 0.4,               # HSV value augmentation
            'copy_paste': 0.0,          # No copy-paste for architectural drawings
            'overlap_mask': True,       # Better mask handling
            'mask_ratio': 4,            # Mask ratio for segmentation
            'dropout': 0.1,             # Add dropout for regularization
            'label_smoothing': 0.1,     # Label smoothing
            'nbs': 64,                  # Nominal batch size
            'hsv_h': 0.015,             # HSV hue augmentation
            'hsv_s': 0.7,               # HSV saturation augmentation
            'hsv_v': 0.4,               # HSV value augmentation
            'degrees': 10.0,            # Rotation augmentation
            'translate': 0.1,           # Translation augmentation
            'scale': 0.5,               # Scale augmentation
            'shear': 2.0,               # Shear augmentation
            'perspective': 0.0001,      # Perspective augmentation
            'flipud': 0.0,              # No vertical flip for architectural drawings
            'fliplr': 0.5,              # Horizontal flip
            'mosaic': 1.0,              # Enable mosaic augmentation
            'mixup': 0.1,               # Add mixup augmentation
            'copy_paste': 0.0           # No copy-paste for architectural drawings
        }
        
        print("🚀 Starting improved YOLOv8 training...")
        print(f"   Model: {self.yolo_model.ckpt_path}")
        print(f"   Epochs: {config['epochs']}")
        print(f"   Batch size: {config['batch']}")
        print(f"   Learning rate: {config['lr0']}")
        
        try:
            # Start training
            results = self.yolo_model.train(**config)
            
            # Save the trained model
            model_path = f"models/{config['name']}.pt"
            os.makedirs("models", exist_ok=True)
            self.yolo_model.save(model_path)
            
            print(f"✅ Improved YOLOv8 training completed!")
            print(f"📁 Model saved to: {model_path}")
            
            return True
            
        except Exception as e:
            print(f"❌ Improved YOLOv8 training failed: {e}")
            return False
    
    def analyze_image_with_clip(self, image_path, detected_objects):
        """Analyze image with CLIP for semantic understanding"""
        if not self.clip_model:
            print("❌ CLIP model not loaded")
            return {}
        
        try:
            # Load image
            image = Image.open(image_path).convert('RGB')
            
            # Prepare text prompts for architectural analysis
            architectural_prompts = [
                "a modern building facade",
                "a traditional architectural style",
                "a residential floor plan",
                "a commercial building",
                "a sustainable design",
                "a minimalist architecture",
                "a classical building",
                "a contemporary design",
                "a functional layout",
                "an aesthetic architectural element",
                "a well-designed space",
                "an efficient floor plan",
                "a beautiful elevation",
                "a professional architectural drawing",
                "a detailed construction plan"
            ]
            
            # Process image and text
            inputs = self.clip_processor(
                text=architectural_prompts,
                images=image,
                return_tensors="pt",
                padding=True
            ).to(self.device)
            
            # Get CLIP predictions
            with torch.no_grad():
                outputs = self.clip_model(**inputs)
                logits_per_image = outputs.logits_per_image
                probs = logits_per_image.softmax(dim=-1)
            
            # Get top predictions
            top_probs, top_indices = torch.topk(probs[0], k=5)
            
            clip_analysis = {
                'style_predictions': [
                    {
                        'prompt': architectural_prompts[idx],
                        'confidence': prob.item()
                    }
                    for prob, idx in zip(top_probs, top_indices)
                ],
                'detected_objects': detected_objects,
                'overall_style_score': float(torch.mean(top_probs))
            }
            
            return clip_analysis
            
        except Exception as e:
            print(f"❌ CLIP analysis failed: {e}")
            return {}
    
    def generate_caption_with_blip(self, image_path):
        """Generate architectural description with BLIP"""
        if not self.blip_model:
            print("❌ BLIP model not loaded")
            return ""
        
        try:
            # Load image
            image = Image.open(image_path).convert('RGB')
            
            # Process image
            inputs = self.blip_processor(image, return_tensors="pt").to(self.device)
            
            # Generate caption with architectural focus
            with torch.no_grad():
                outputs = self.blip_model.generate(
                    **inputs, 
                    max_length=100, 
                    num_beams=5,
                    do_sample=True,
                    temperature=0.7,
                    top_p=0.9
                )
                caption = self.blip_processor.decode(outputs[0], skip_special_tokens=True)
            
            return caption
            
        except Exception as e:
            print(f"❌ BLIP caption generation failed: {e}")
            return ""
    
    def comprehensive_analysis(self, image_path):
        """Perform comprehensive architectural analysis"""
        print(f"\n🔍 IMPROVED COMPREHENSIVE ANALYSIS: {Path(image_path).name}")
        print("=" * 60)
        
        # 1. YOLO Object Detection
        print("1️⃣ Running improved YOLO object detection...")
        if not self.yolo_model:
            print("❌ YOLO model not trained yet")
            return
        
        results = self.yolo_model(image_path, conf=0.25, iou=0.45)
        detections = []
        
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    conf = box.conf[0].cpu().numpy()
                    cls = int(box.cls[0].cpu().numpy())
                    
                    detection = {
                        'bbox': [x1, y1, x2, y2],
                        'confidence': conf,
                        'class_id': cls,
                        'class_name': self.class_names[cls] if cls < len(self.class_names) else f"class_{cls}"
                    }
                    detections.append(detection)
        
        print(f"   Detected {len(detections)} objects")
        
        # 2. CLIP Semantic Analysis
        print("2️⃣ Running improved CLIP semantic analysis...")
        clip_analysis = self.analyze_image_with_clip(image_path, detections)
        
        # 3. BLIP Caption Generation
        print("3️⃣ Generating improved BLIP caption...")
        blip_caption = self.generate_caption_with_blip(image_path)
        
        # 4. Compile Results
        analysis_results = {
            'image_path': image_path,
            'yolo_detections': detections,
            'clip_analysis': clip_analysis,
            'blip_caption': blip_caption,
            'comprehensive_summary': self.generate_improved_summary(detections, clip_analysis, blip_caption)
        }
        
        # 5. Display Results
        self.display_improved_results(analysis_results)
        
        return analysis_results
    
    def generate_improved_summary(self, detections, clip_analysis, blip_caption):
        """Generate improved comprehensive summary"""
        summary = {
            'total_elements': len(detections),
            'element_types': {},
            'confidence_stats': {},
            'style_analysis': {},
            'architectural_assessment': {}
        }
        
        # Element type analysis
        for det in detections:
            element_type = det['class_name']
            if element_type not in summary['element_types']:
                summary['element_types'][element_type] = 0
            summary['element_types'][element_type] += 1
        
        # Confidence statistics
        if detections:
            confidences = [d['confidence'] for d in detections]
            summary['confidence_stats'] = {
                'average_confidence': np.mean(confidences),
                'max_confidence': np.max(confidences),
                'min_confidence': np.min(confidences),
                'high_confidence_count': len([c for c in confidences if c > 0.7])
            }
        
        # Style analysis from CLIP
        if clip_analysis and 'style_predictions' in clip_analysis:
            summary['style_analysis'] = {
                'top_styles': clip_analysis['style_predictions'][:3],
                'overall_style_score': clip_analysis.get('overall_style_score', 0)
            }
        
        # Architectural assessment
        summary['architectural_assessment'] = {
            'drawing_quality': 'Good' if len(detections) > 5 else 'Needs improvement',
            'element_diversity': len(summary['element_types']),
            'detection_confidence': summary['confidence_stats'].get('average_confidence', 0),
            'style_coherence': summary['style_analysis'].get('overall_style_score', 0)
        }
        
        return summary
    
    def display_improved_results(self, analysis_results):
        """Display improved analysis results"""
        print(f"\n📊 IMPROVED ANALYSIS RESULTS")
        print("=" * 50)
        
        summary = analysis_results['comprehensive_summary']
        
        print(f"🏗️ Element Detection:")
        print(f"   Total elements: {summary['total_elements']}")
        print(f"   Element types: {len(summary['element_types'])}")
        
        if summary['element_types']:
            print(f"   Most common elements:")
            sorted_elements = sorted(summary['element_types'].items(), key=lambda x: x[1], reverse=True)
            for element, count in sorted_elements[:5]:
                print(f"     {element}: {count}")
        
        print(f"\n🎯 Confidence Statistics:")
        conf_stats = summary['confidence_stats']
        print(f"   Average confidence: {conf_stats.get('average_confidence', 0):.3f}")
        print(f"   High confidence detections: {conf_stats.get('high_confidence_count', 0)}")
        
        print(f"\n🎨 Style Analysis:")
        style_analysis = summary['style_analysis']
        if 'top_styles' in style_analysis:
            print(f"   Top architectural styles:")
            for style in style_analysis['top_styles']:
                print(f"     {style['prompt']}: {style['confidence']:.3f}")
        
        print(f"\n📝 BLIP Caption:")
        print(f"   {analysis_results['blip_caption']}")
        
        print(f"\n🏆 Architectural Assessment:")
        assessment = summary['architectural_assessment']
        print(f"   Drawing Quality: {assessment['drawing_quality']}")
        print(f"   Element Diversity: {assessment['element_diversity']}")
        print(f"   Detection Confidence: {assessment['detection_confidence']:.3f}")
        print(f"   Style Coherence: {assessment['style_coherence']:.3f}")
    
    def run_improved_pipeline(self):
        """Run the complete improved training and analysis pipeline"""
        print("🚀 IMPROVED ARCHITECTURAL ANALYSIS PIPELINE")
        print("=" * 60)
        
        # 1. Load CLIP and BLIP models
        print("\n1️⃣ Loading semantic models...")
        clip_loaded = self.load_clip_model()
        blip_loaded = self.load_blip_model()
        
        # 2. Train improved YOLO model
        print("\n2️⃣ Training improved YOLO model...")
        yolo_trained = self.train_improved_yolo_model()
        
        if not yolo_trained:
            print("❌ Improved YOLO training failed. Cannot proceed with analysis.")
            return False
        
        # 3. Test on sample images
        print("\n3️⃣ Testing improved analysis...")
        test_images = list(Path("images/train").glob("*.jpg")) + list(Path("images/train").glob("*.png"))
        
        if len(test_images) > 0:
            # Test on first image
            test_image = str(test_images[0])
            print(f"🔍 Testing on: {Path(test_image).name}")
            
            analysis_results = self.comprehensive_analysis(test_image)
            
            if analysis_results:
                print("✅ Improved analysis completed successfully!")
                return True
        
        return False

def main():
    """Main function"""
    print("🚀 IMPROVED ARCHITECTURAL TRAINING SYSTEM")
    print("=" * 60)
    
    # Initialize improved trainer
    trainer = ImprovedArchitecturalTrainer()
    
    # Run improved pipeline
    success = trainer.run_improved_pipeline()
    
    if success:
        print("\n🎉 Improved pipeline completed successfully!")
    else:
        print("\n❌ Improved pipeline failed!")

if __name__ == "__main__":
    main() 