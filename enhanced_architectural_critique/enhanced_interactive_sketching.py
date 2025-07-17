#!/usr/bin/env python3
"""
Enhanced Interactive SAM Sketching System
Uses the enhanced model manager with SDXL-style organization
"""

import cv2
import numpy as np
import torch
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import os
import json
from typing import List, Tuple, Optional, Dict, Any
import threading
import queue
import time
from pathlib import Path

# Import our enhanced model manager
from enhanced_model_manager import EnhancedModelManager, get_model_manager

class EnhancedInteractiveSAMSketcher:
    """
    Enhanced interactive SAM-based sketching system with SDXL-style organization
    """
    
    def __init__(self, config_path: str = "sketching_config.json"):
        """
        Initialize the enhanced interactive SAM sketcher
        
        Args:
            config_path: Path to configuration file
        """
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Initialize model manager
        self.model_manager = get_model_manager()
        
        # Image and drawing state
        self.current_image = None
        self.original_image = None
        self.drawing_image = None
        self.drawing = False
        self.last_x = None
        self.last_y = None
        
        # Drawing parameters
        self.brush_size = self.config.get('drawing', {}).get('brush_size', 5)
        self.brush_color = tuple(self.config.get('drawing', {}).get('brush_color', [0, 255, 0]))
        self.drawing_mode = self.config.get('drawing', {}).get('drawing_mode', 'sketch')
        
        # SAM interaction points
        self.input_points = []
        self.input_labels = []
        self.input_boxes = []
        
        # Results
        self.current_mask = None
        self.mask_history = []
        
        # GUI elements
        self.root = None
        self.canvas = None
        self.photo = None
        
        # Analysis results
        self.detected_objects = []
        self.analysis_results = {}
        
        # Performance tracking
        self.processing_times = []
        
        print("🎨 Enhanced Interactive SAM Sketcher initialized")
        print(f"   Device: {self.model_manager.config.device}")
        print(f"   Drawing mode: {self.drawing_mode}")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from file"""
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
        else:
            # Default configuration
            return {
                'models': {
                    'sam_checkpoint': 'sam_vit_h_4b8939.pth',
                    'yolo_model_path': '../shared/yolov8n.pt',
                    'device': 'auto',
                    'confidence_threshold': 0.5
                },
                'drawing': {
                    'brush_size': 5,
                    'brush_color': [0, 255, 0],
                    'drawing_mode': 'sketch'
                },
                'analysis': {
                    'enable_object_detection': True,
                    'enable_segmentation': True,
                    'enable_spatial_analysis': True
                },
                'performance': {
                    'enable_caching': True,
                    'max_image_size': 1024,
                    'batch_processing': False
                }
            }
    
    def load_models(self):
        """Load required models using the enhanced model manager"""
        print("🔁 Loading models...")
        
        try:
            # Load YOLO model
            if self.config.get('analysis', {}).get('enable_object_detection', True):
                self.model_manager.load_yolo_model()
                print("✅ YOLO model loaded")
            
            # Load SAM model
            if self.config.get('analysis', {}).get('enable_segmentation', True):
                sam_path = self.config.get('models', {}).get('sam_checkpoint', 'sam_vit_h_4b8939.pth')
                self.model_manager.load_sam_model(sam_path)
                print("✅ SAM model loaded")
            
            # Print memory info
            memory_info = self.model_manager.get_memory_info()
            print(f"📊 Memory usage: {memory_info.get('gpu_memory_allocated', 0):.2f} GB")
            
        except Exception as e:
            print(f"❌ Error loading models: {e}")
            raise
    
    def load_image(self, image_path: str) -> np.ndarray:
        """Load and preprocess image with enhanced preprocessing"""
        print(f"📸 Loading image: {image_path}")
        
        # Load image
        self.original_image = cv2.imread(image_path)
        if self.original_image is None:
            raise ValueError(f"Could not load image from {image_path}")
        
        # Enhanced preprocessing
        self.current_image = self._preprocess_image(self.original_image)
        self.drawing_image = self.current_image.copy()
        
        # Set image for SAM if available
        if self.model_manager.sam_predictor:
            rgb_image = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2RGB)
            self.model_manager.sam_predictor.set_image(rgb_image)
            print("✅ Image set for SAM")
        
        return self.current_image
    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Enhanced image preprocessing for better detection"""
        # Resize if too large
        max_size = self.config.get('performance', {}).get('max_image_size', 1024)
        height, width = image.shape[:2]
        
        if max(height, width) > max_size:
            scale = max_size / max(height, width)
            new_width = int(width * scale)
            new_height = int(height * scale)
            image = cv2.resize(image, (new_width, new_height))
            print(f"📏 Resized image to {new_width}x{new_height}")
        
        # Convert to RGB for better processing
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
        lab = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2LAB)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        lab[:,:,0] = clahe.apply(lab[:,:,0])
        enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
        
        # Convert back to BGR for OpenCV compatibility
        return cv2.cvtColor(enhanced, cv2.COLOR_RGB2BGR)
    
    def detect_objects(self, confidence_threshold: float = 0.5) -> List[Dict[str, Any]]:
        """Enhanced object detection with performance tracking"""
        if self.current_image is None:
            raise ValueError("No image loaded")
        
        if not self.model_manager.yolo_model:
            print("⚠️ YOLO model not available")
            return []
        
        start_time = time.time()
        
        try:
            results = self.model_manager.yolo_model(self.current_image)
            self.detected_objects = []
            
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        # Extract box coordinates and confidence
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        confidence = box.conf[0].cpu().numpy()
                        class_id = int(box.cls[0].cpu().numpy())
                        class_name = self.model_manager.yolo_model.names[class_id]
                        
                        if confidence >= confidence_threshold:
                            detected_obj = {
                                'bbox': (int(x1), int(y1), int(x2), int(y2)),
                                'confidence': float(confidence),
                                'class_name': class_name,
                                'center': (int((x1 + x2) / 2), int((y1 + y2) / 2)),
                                'area': float((x2 - x1) * (y2 - y1))
                            }
                            self.detected_objects.append(detected_obj)
            
            processing_time = time.time() - start_time
            self.processing_times.append(('object_detection', processing_time))
            print(f"✅ Detected {len(self.detected_objects)} objects in {processing_time:.3f}s")
            
            return self.detected_objects
            
        except Exception as e:
            print(f"❌ Error during object detection: {e}")
            return []
    
    def segment_sketch(self, points: List[Tuple[int, int]], labels: List[int]) -> np.ndarray:
        """Segment based on sketch points using SAM"""
        if not self.model_manager.sam_predictor:
            print("⚠️ SAM model not available")
            return None
        
        if not points:
            return None
        
        start_time = time.time()
        
        try:
            # Convert points to numpy array
            input_points = np.array(points)
            input_labels = np.array(labels)
            
            # Predict mask
            masks, scores, logits = self.model_manager.sam_predictor.predict(
                point_coords=input_points,
                point_labels=input_labels,
                multimask_output=False,
            )
            
            # Use the best mask
            mask = masks[0]
            
            processing_time = time.time() - start_time
            self.processing_times.append(('segmentation', processing_time))
            print(f"✅ Segmentation completed in {processing_time:.3f}s")
            
            return mask
            
        except Exception as e:
            print(f"❌ Error during segmentation: {e}")
            return None
    
    def create_gui(self):
        """Create enhanced GUI with better organization"""
        self.root = tk.Tk()
        self.root.title("Enhanced Interactive SAM Sketcher")
        self.root.geometry("1200x800")
        
        # Configure grid weights
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Create left panel for controls
        self._create_control_panel()
        
        # Create main canvas area
        self._create_canvas_area()
        
        # Create right panel for results
        self._create_results_panel()
        
        # Bind events
        self._bind_events()
        
        print("✅ GUI created successfully")
    
    def _create_control_panel(self):
        """Create left control panel"""
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.grid(row=0, column=0, sticky="nsew")
        
        # Title
        title_label = ttk.Label(control_frame, text="🎨 Enhanced SAM Sketcher", font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # File operations
        file_frame = ttk.LabelFrame(control_frame, text="📁 File Operations", padding="10")
        file_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Button(file_frame, text="Load Image", command=self._load_image_gui).pack(fill="x", pady=2)
        ttk.Button(file_frame, text="Save Results", command=self._save_results_gui).pack(fill="x", pady=2)
        ttk.Button(file_frame, text="Export Mask", command=self._export_mask_gui).pack(fill="x", pady=2)
        
        # Drawing controls
        drawing_frame = ttk.LabelFrame(control_frame, text="✏️ Drawing Controls", padding="10")
        drawing_frame.pack(fill="x", pady=(0, 10))
        
        # Brush size
        ttk.Label(drawing_frame, text="Brush Size:").pack(anchor="w")
        self.brush_size_var = tk.IntVar(value=self.brush_size)
        brush_slider = ttk.Scale(drawing_frame, from_=1, to=20, variable=self.brush_size_var, 
                                orient="horizontal", command=self._update_brush_size)
        brush_slider.pack(fill="x", pady=(0, 10))
        
        # Drawing mode
        ttk.Label(drawing_frame, text="Drawing Mode:").pack(anchor="w")
        self.mode_var = tk.StringVar(value=self.drawing_mode)
        mode_combo = ttk.Combobox(drawing_frame, textvariable=self.mode_var, 
                                 values=["sketch", "point", "box"], state="readonly")
        mode_combo.pack(fill="x", pady=(0, 10))
        mode_combo.bind("<<ComboboxSelected>>", self._update_drawing_mode)
        
        # Analysis controls
        analysis_frame = ttk.LabelFrame(control_frame, text="🔍 Analysis", padding="10")
        analysis_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Button(analysis_frame, text="Detect Objects", command=self._detect_objects_gui).pack(fill="x", pady=2)
        ttk.Button(analysis_frame, text="Segment Sketch", command=self._segment_sketch_gui).pack(fill="x", pady=2)
        ttk.Button(analysis_frame, text="Clear Results", command=self._clear_results).pack(fill="x", pady=2)
        
        # Performance info
        perf_frame = ttk.LabelFrame(control_frame, text="⚡ Performance", padding="10")
        perf_frame.pack(fill="x", pady=(0, 10))
        
        self.perf_label = ttk.Label(perf_frame, text="Ready")
        self.perf_label.pack()
        
        # Memory info
        self.memory_label = ttk.Label(perf_frame, text="")
        self.memory_label.pack()
        self._update_memory_info()
    
    def _create_canvas_area(self):
        """Create main canvas area"""
        canvas_frame = ttk.Frame(self.root)
        canvas_frame.grid(row=0, column=1, sticky="nsew", padx=10)
        canvas_frame.grid_columnconfigure(0, weight=1)
        canvas_frame.grid_rowconfigure(0, weight=1)
        
        # Create canvas with scrollbars
        canvas_container = ttk.Frame(canvas_frame)
        canvas_container.grid(row=0, column=0, sticky="nsew")
        canvas_container.grid_columnconfigure(0, weight=1)
        canvas_container.grid_rowconfigure(0, weight=1)
        
        # Scrollbars
        h_scrollbar = ttk.Scrollbar(canvas_container, orient="horizontal")
        v_scrollbar = ttk.Scrollbar(canvas_container, orient="vertical")
        
        # Canvas
        self.canvas = tk.Canvas(canvas_container, bg="white", 
                               xscrollcommand=h_scrollbar.set,
                               yscrollcommand=v_scrollbar.set)
        
        # Configure scrollbars
        h_scrollbar.config(command=self.canvas.xview)
        v_scrollbar.config(command=self.canvas.yview)
        
        # Grid layout
        self.canvas.grid(row=0, column=0, sticky="nsew")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
    
    def _create_results_panel(self):
        """Create right results panel"""
        results_frame = ttk.Frame(self.root, padding="10")
        results_frame.grid(row=0, column=2, sticky="nsew")
        
        # Title
        results_title = ttk.Label(results_frame, text="📊 Results", font=("Arial", 12, "bold"))
        results_title.pack(pady=(0, 10))
        
        # Results text
        self.results_text = tk.Text(results_frame, width=30, height=20, wrap="word")
        results_scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.results_text.yview)
        self.results_text.config(yscrollcommand=results_scrollbar.set)
        
        self.results_text.pack(side="left", fill="both", expand=True)
        results_scrollbar.pack(side="right", fill="y")
    
    def _bind_events(self):
        """Bind canvas events"""
        self.canvas.bind("<Button-1>", self._on_mouse_down)
        self.canvas.bind("<B1-Motion>", self._on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_mouse_up)
        self.canvas.bind("<Button-3>", self._on_right_click)
    
    def _update_brush_size(self, value):
        """Update brush size"""
        self.brush_size = int(float(value))
    
    def _update_drawing_mode(self, event):
        """Update drawing mode"""
        self.drawing_mode = self.mode_var.get()
    
    def _update_memory_info(self):
        """Update memory information display"""
        try:
            memory_info = self.model_manager.get_memory_info()
            if 'gpu_memory_allocated' in memory_info:
                text = f"GPU: {memory_info['gpu_memory_allocated']:.2f} GB"
                if 'gpu_name' in memory_info:
                    text += f"\n{memory_info['gpu_name']}"
            else:
                text = f"Device: {memory_info['device']}"
            
            self.memory_label.config(text=text)
        except Exception as e:
            self.memory_label.config(text=f"Error: {e}")
        
        # Update every 5 seconds
        self.root.after(5000, self._update_memory_info)
    
    def _load_image_gui(self):
        """Load image through GUI"""
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff")]
        )
        
        if file_path:
            try:
                self.load_image(file_path)
                self._display_image()
                self._log_result(f"Loaded image: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not load image: {e}")
    
    def _display_image(self):
        """Display image on canvas"""
        if self.drawing_image is None:
            return
        
        # Convert BGR to RGB
        rgb_image = cv2.cvtColor(self.drawing_image, cv2.COLOR_BGR2RGB)
        
        # Convert to PIL Image
        pil_image = Image.fromarray(rgb_image)
        
        # Resize if too large for canvas
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width > 1 and canvas_height > 1:
            # Calculate scale to fit canvas
            img_width, img_height = pil_image.size
            scale_x = canvas_width / img_width
            scale_y = canvas_height / img_height
            scale = min(scale_x, scale_y, 1.0)  # Don't scale up
            
            if scale < 1.0:
                new_width = int(img_width * scale)
                new_height = int(img_height * scale)
                pil_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Convert to PhotoImage
        self.photo = ImageTk.PhotoImage(pil_image)
        
        # Clear canvas and display image
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.photo)
        
        # Configure scroll region
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
    
    def _on_mouse_down(self, event):
        """Handle mouse down event"""
        self.drawing = True
        self.last_x = event.x
        self.last_y = event.y
        
        # Add point for segmentation
        if self.drawing_mode == "point":
            self.input_points.append((event.x, event.y))
            self.input_labels.append(1)  # Positive point
            self._draw_point(event.x, event.y)
    
    def _on_mouse_drag(self, event):
        """Handle mouse drag event"""
        if not self.drawing:
            return
        
        if self.drawing_mode == "sketch":
            # Draw line
            self.canvas.create_line(self.last_x, self.last_y, event.x, event.y,
                                  fill="green", width=self.brush_size, smooth=True)
            
            # Add points for segmentation
            self.input_points.append((event.x, event.y))
            self.input_labels.append(1)  # Positive point
        
        self.last_x = event.x
        self.last_y = event.y
    
    def _on_mouse_up(self, event):
        """Handle mouse up event"""
        self.drawing = False
    
    def _on_right_click(self, event):
        """Handle right click (negative point)"""
        self.input_points.append((event.x, event.y))
        self.input_labels.append(0)  # Negative point
        self._draw_point(event.x, event.y, color="red")
    
    def _draw_point(self, x, y, color="green"):
        """Draw a point on canvas"""
        size = self.brush_size
        self.canvas.create_oval(x-size, y-size, x+size, y+size, 
                              fill=color, outline=color)
    
    def _detect_objects_gui(self):
        """Detect objects through GUI"""
        if self.current_image is None:
            messagebox.showwarning("Warning", "Please load an image first")
            return
        
        try:
            confidence = self.config.get('models', {}).get('confidence_threshold', 0.5)
            objects = self.detect_objects(confidence)
            
            # Display results
            self._display_detections(objects)
            self._log_result(f"Detected {len(objects)} objects")
            
        except Exception as e:
            messagebox.showerror("Error", f"Detection failed: {e}")
    
    def _display_detections(self, objects):
        """Display detected objects on canvas"""
        for i, obj in enumerate(objects):
            x1, y1, x2, y2 = obj['bbox']
            class_name = obj['class_name']
            confidence = obj['confidence']
            
            # Draw bounding box
            self.canvas.create_rectangle(x1, y1, x2, y2, outline="blue", width=2)
            
            # Draw label
            label = f"{class_name} ({confidence:.2f})"
            self.canvas.create_text(x1, y1-10, anchor="sw", text=label, 
                                  fill="blue", font=("Arial", 8))
    
    def _segment_sketch_gui(self):
        """Segment sketch through GUI"""
        if not self.input_points:
            messagebox.showwarning("Warning", "Please draw some points or lines first")
            return
        
        try:
            mask = self.segment_sketch(self.input_points, self.input_labels)
            
            if mask is not None:
                self.current_mask = mask
                self._display_mask(mask)
                self._log_result("Segmentation completed")
            else:
                messagebox.showwarning("Warning", "Segmentation failed")
                
        except Exception as e:
            messagebox.showerror("Error", f"Segmentation failed: {e}")
    
    def _display_mask(self, mask):
        """Display segmentation mask on canvas"""
        if mask is None:
            return
        
        # Convert mask to image
        mask_image = (mask * 255).astype(np.uint8)
        mask_image = cv2.cvtColor(mask_image, cv2.COLOR_GRAY2RGB)
        
        # Create overlay
        overlay = np.zeros_like(self.drawing_image)
        overlay[mask] = [0, 255, 0]  # Green overlay
        
        # Blend with original image
        alpha = 0.3
        blended = cv2.addWeighted(self.drawing_image, 1-alpha, overlay, alpha, 0)
        
        # Update drawing image
        self.drawing_image = blended
        self._display_image()
    
    def _clear_results(self):
        """Clear all results"""
        self.input_points = []
        self.input_labels = []
        self.current_mask = None
        self.detected_objects = []
        
        # Reset drawing image to original
        if self.original_image is not None:
            self.drawing_image = self.original_image.copy()
            self._display_image()
        
        self._log_result("Results cleared")
    
    def _save_results_gui(self):
        """Save results through GUI"""
        if not self.detected_objects and self.current_mask is None:
            messagebox.showwarning("Warning", "No results to save")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Save Results",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self._save_results(file_path)
                self._log_result(f"Results saved to {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save results: {e}")
    
    def _save_results(self, file_path: str):
        """Save analysis results to file"""
        results = {
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
            'image_path': getattr(self, 'current_image_path', 'unknown'),
            'detected_objects': self.detected_objects,
            'processing_times': self.processing_times,
            'config': self.config
        }
        
        with open(file_path, 'w') as f:
            json.dump(results, f, indent=2)
    
    def _export_mask_gui(self):
        """Export mask through GUI"""
        if self.current_mask is None:
            messagebox.showwarning("Warning", "No mask to export")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Export Mask",
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                mask_image = (self.current_mask * 255).astype(np.uint8)
                cv2.imwrite(file_path, mask_image)
                self._log_result(f"Mask exported to {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not export mask: {e}")
    
    def _log_result(self, message: str):
        """Log result message"""
        timestamp = time.strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        self.results_text.insert("end", log_message)
        self.results_text.see("end")
        
        print(log_message.strip())
    
    def run(self):
        """Run the enhanced interactive sketching system"""
        print("🚀 Starting Enhanced Interactive SAM Sketcher...")
        
        # Load models
        try:
            self.load_models()
        except Exception as e:
            print(f"❌ Failed to load models: {e}")
            messagebox.showerror("Error", f"Failed to load models: {e}")
            return
        
        # Create GUI
        self.create_gui()
        
        # Start GUI
        print("✅ GUI ready. Starting main loop...")
        self.root.mainloop()
    
    def cleanup(self):
        """Cleanup resources"""
        print("🧹 Cleaning up resources...")
        
        # Unload models
        if self.model_manager:
            self.model_manager.unload_all_models()
        
        print("✅ Cleanup completed")

def main():
    """Main function"""
    print("🎨 Enhanced Interactive SAM Sketching System")
    print("=" * 50)
    
    # Create sketcher
    sketcher = EnhancedInteractiveSAMSketcher()
    
    try:
        # Run the system
        sketcher.run()
    except KeyboardInterrupt:
        print("\n⚠️ Interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        # Cleanup
        sketcher.cleanup()

if __name__ == "__main__":
    main() 