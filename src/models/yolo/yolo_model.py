import os
import sys

# Configure environment for E drive storage
def setup_e_drive_environment():
    """Set up environment variables to use E drive for storage"""
    e_drive_base = "E:/macad-thesis-25"
    cache_dir = os.path.join(e_drive_base, "cache")
    
    # Create directories if they don't exist
    os.makedirs(cache_dir, exist_ok=True)
    
    # Set environment variables
    os.environ['TORCH_HOME'] = os.path.join(cache_dir, "torch")
    os.environ['YOLO_CACHE_DIR'] = os.path.join(cache_dir, "yolo")
    
    # Create subdirectories
    os.makedirs(os.environ['TORCH_HOME'], exist_ok=True)
    os.makedirs(os.environ['YOLO_CACHE_DIR'], exist_ok=True)
    
    print(f"Using E drive for YOLO model storage: {cache_dir}")

# Set up environment before importing ultralytics
setup_e_drive_environment()

from ultralytics import YOLO

class YOLOModel:
    def __init__(self, model_path="yolov8n.pt"):
        """
        Initialize YOLO model for object detection
        
        Args:
            model_path (str): Path to YOLO model weights file
        """
        self.model_path = model_path
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the YOLO model"""
        try:
            # Set cache directory for YOLO
            cache_dir = os.environ.get('YOLO_CACHE_DIR')
            if cache_dir:
                os.environ['YOLO_CACHE_DIR'] = cache_dir
            
            self.model = YOLO(self.model_path)
            print(f"YOLO model loaded successfully from {self.model_path}")
            print(f"Cache location: {cache_dir}")
        except Exception as e:
            print(f"Error loading YOLO model: {e}")
            # Fallback to default model if custom model fails
            self.model = YOLO("yolov8n.pt")
            print("Using default YOLOv8n model")
    
    def detect(self, image_path):
        """
        Perform object detection on an image
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            tuple: (boxes, classes, confidences) - detected bounding boxes, class labels, and confidence scores
        """
        if self.model is None:
            raise ValueError("Model not loaded")
        
        try:
            results = self.model(image_path)
            boxes = results[0].boxes.xyxy.cpu().numpy()
            classes = results[0].boxes.cls.cpu().numpy()
            confidences = results[0].boxes.conf.cpu().numpy()
            
            return boxes, classes, confidences
        except Exception as e:
            print(f"Error during detection: {e}")
            return [], [], []
    
    def get_class_names(self):
        """Get the class names for the model"""
        if self.model is None:
            return []
        return self.model.names

# Global model instance
yolo_model = YOLOModel() 