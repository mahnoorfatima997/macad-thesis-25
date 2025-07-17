#!/usr/bin/env python3
"""
Enhanced Model Manager for Architectural AI
Incorporates best practices from SDXL-style model management
"""

import os
import torch
import json
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, field
import gc

# Import required libraries
try:
    from ultralytics import YOLO
    from segment_anything import sam_model_registry, SamPredictor
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    print("⚠️ YOLO not available")

try:
    from diffusers import StableDiffusionXLControlNetPipeline, ControlNetModel, AutoencoderKL
    from transformers import AutoImageProcessor, AutoModelForDepthEstimation
    DIFFUSERS_AVAILABLE = True
except ImportError:
    DIFFUSERS_AVAILABLE = False
    print("⚠️ Diffusers not available")

@dataclass
class ModelPaths:
    """Centralized model path configuration"""
    # Core models
    yolo_model_path: str = "./shared/yolov8n.pt"
    sam_checkpoint: str = "./sam_vit_h_4b8939.pth"
    
    # SDXL models (optional)
    sdxl_base_path: str = "./models/sdxl-base"
    sdxl_vae_path: str = "./models/sdxl-vae"
    controlnet_depth_path: str = "./models/controlnet-depth"
    depth_model_path: str = "./models/depth-anything"
    
    # Cache directories
    cache_dir: str = "./cache"
    model_cache_dir: str = "./cache/models"
    
    def __post_init__(self):
        """Create directories if they don't exist"""
        for path in [self.cache_dir, self.model_cache_dir]:
            Path(path).mkdir(parents=True, exist_ok=True)

@dataclass
class ModelConfig:
    """Model configuration settings"""
    device: str = "auto"  # auto, cuda, cpu, mps
    torch_dtype: str = "auto"  # auto, float16, float32
    use_half_precision: bool = True
    enable_cache: bool = True
    max_memory_usage: float = 0.8  # Maximum GPU memory usage (0.8 = 80%)
    
    def __post_init__(self):
        """Set device and dtype automatically"""
        if self.device == "auto":
            if torch.cuda.is_available():
                self.device = "cuda"
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                self.device = "mps"
            else:
                self.device = "cpu"
        
        if self.torch_dtype == "auto":
            if self.device == "cuda" and self.use_half_precision:
                self.torch_dtype = torch.float16
            else:
                self.torch_dtype = torch.float32

class EnhancedModelManager:
    """
    Enhanced model manager with SDXL-style organization
    """
    
    def __init__(self, config: Optional[ModelConfig] = None, paths: Optional[ModelPaths] = None):
        """
        Initialize the enhanced model manager
        
        Args:
            config: Model configuration
            paths: Model paths configuration
        """
        self.config = config or ModelConfig()
        self.paths = paths or ModelPaths()
        
        # Model instances
        self.yolo_model: Optional[Any] = None
        self.sam_predictor: Optional[Any] = None
        self.sdxl_pipeline: Optional[Any] = None
        self.depth_model: Optional[Any] = None
        self.depth_processor: Optional[Any] = None
        
        # Loaded models tracking
        self.loaded_models: Dict[str, bool] = {
            'yolo': False,
            'sam': False,
            'sdxl': False,
            'depth': False
        }
        
        print(f"🔧 Enhanced Model Manager initialized")
        print(f"   Device: {self.config.device}")
        print(f"   Dtype: {self.config.torch_dtype}")
        print(f"   Cache: {self.paths.cache_dir}")
    
    def load_yolo_model(self, model_path: Optional[str] = None) -> Any:
        """Load YOLO model with enhanced memory management"""
        if not YOLO_AVAILABLE:
            raise ImportError("YOLO not available. Install with: pip install ultralytics")
        
        if self.yolo_model is not None:
            return self.yolo_model
        
        model_path = model_path or self.paths.yolo_model_path
        print(f"🔁 Loading YOLO model: {model_path}")
        
        try:
            # Set cache directory
            os.environ['YOLO_CACHE_DIR'] = self.paths.model_cache_dir
            
            self.yolo_model = YOLO(model_path)
            self.loaded_models['yolo'] = True
            print("✅ YOLO model loaded successfully")
            
            return self.yolo_model
            
        except Exception as e:
            print(f"❌ Error loading YOLO model: {e}")
            raise
    
    def load_sam_model(self, checkpoint_path: Optional[str] = None) -> Any:
        """Load SAM model with enhanced memory management"""
        checkpoint_path = checkpoint_path or self.paths.sam_checkpoint
        
        if not os.path.exists(checkpoint_path):
            raise FileNotFoundError(f"SAM checkpoint not found: {checkpoint_path}")
        
        if self.sam_predictor is not None:
            return self.sam_predictor
        
        print(f"🔁 Loading SAM model: {checkpoint_path}")
        
        try:
            model_type = "vit_h"
            sam = sam_model_registry[model_type](checkpoint=checkpoint_path)
            sam.to(device=self.config.device)
            self.sam_predictor = SamPredictor(sam)
            self.loaded_models['sam'] = True
            print("✅ SAM model loaded successfully")
            
            return self.sam_predictor
            
        except Exception as e:
            print(f"❌ Error loading SAM model: {e}")
            raise
    
    def load_sdxl_pipeline(self, base_path: Optional[str] = None) -> Any:
        """Load SDXL pipeline with ControlNet (optional)"""
        if not DIFFUSERS_AVAILABLE:
            raise ImportError("Diffusers not available. Install with: pip install diffusers")
        
        base_path = base_path or self.paths.sdxl_base_path
        
        if self.sdxl_pipeline is not None:
            return self.sdxl_pipeline
        
        print(f"🔁 Loading SDXL pipeline: {base_path}")
        
        try:
            # Load ControlNet if available
            controlnet = None
            if os.path.exists(self.paths.controlnet_depth_path):
                controlnet = ControlNetModel.from_pretrained(
                    self.paths.controlnet_depth_path,
                    torch_dtype=self.config.torch_dtype
                )
                print("✅ ControlNet loaded")
            
            # Load VAE if available
            vae = None
            if os.path.exists(self.paths.sdxl_vae_path):
                vae = AutoencoderKL.from_pretrained(
                    self.paths.sdxl_vae_path,
                    torch_dtype=self.config.torch_dtype
                )
                print("✅ VAE loaded")
            
            # Load pipeline
            if os.path.exists(base_path):
                self.sdxl_pipeline = StableDiffusionXLControlNetPipeline.from_pretrained(
                    base_path,
                    controlnet=controlnet,
                    vae=vae,
                    torch_dtype=self.config.torch_dtype
                )
            else:
                # Load from HuggingFace
                self.sdxl_pipeline = StableDiffusionXLControlNetPipeline.from_pretrained(
                    "stabilityai/stable-diffusion-xl-base-1.0",
                    controlnet=controlnet,
                    vae=vae,
                    torch_dtype=self.config.torch_dtype
                )
            
            self.sdxl_pipeline.to(device=self.config.device)
            self.loaded_models['sdxl'] = True
            print("✅ SDXL pipeline loaded successfully")
            
            return self.sdxl_pipeline
            
        except Exception as e:
            print(f"❌ Error loading SDXL pipeline: {e}")
            raise
    
    def load_depth_model(self, model_path: Optional[str] = None) -> tuple:
        """Load depth estimation model"""
        if not DIFFUSERS_AVAILABLE:
            raise ImportError("Transformers not available")
        
        model_path = model_path or self.paths.depth_model_path
        
        if self.depth_model is not None and self.depth_processor is not None:
            return self.depth_processor, self.depth_model
        
        print(f"🔁 Loading depth model: {model_path}")
        
        try:
            if os.path.exists(model_path):
                processor = AutoImageProcessor.from_pretrained(model_path)
                model = AutoModelForDepthEstimation.from_pretrained(
                    model_path, 
                    torch_dtype=self.config.torch_dtype
                )
            else:
                # Load from HuggingFace
                processor = AutoImageProcessor.from_pretrained("LiheYoung/depth-anything-large-hf")
                model = AutoModelForDepthEstimation.from_pretrained(
                    "LiheYoung/depth-anything-large-hf",
                    torch_dtype=self.config.torch_dtype
                )
            
            model.to(device=self.config.device)
            self.depth_processor = processor
            self.depth_model = model
            self.loaded_models['depth'] = True
            print("✅ Depth model loaded successfully")
            
            return processor, model
            
        except Exception as e:
            print(f"❌ Error loading depth model: {e}")
            raise
    
    def load_all_models(self) -> Dict[str, Any]:
        """Load all available models"""
        models = {}
        
        try:
            models['yolo'] = self.load_yolo_model()
        except Exception as e:
            print(f"⚠️ Could not load YOLO: {e}")
        
        try:
            models['sam'] = self.load_sam_model()
        except Exception as e:
            print(f"⚠️ Could not load SAM: {e}")
        
        try:
            models['sdxl'] = self.load_sdxl_pipeline()
        except Exception as e:
            print(f"⚠️ Could not load SDXL: {e}")
        
        try:
            models['depth'] = self.load_depth_model()
        except Exception as e:
            print(f"⚠️ Could not load depth model: {e}")
        
        return models
    
    def unload_model(self, model_name: str):
        """Unload a specific model to free memory"""
        if model_name == 'yolo' and self.yolo_model is not None:
            del self.yolo_model
            self.yolo_model = None
            self.loaded_models['yolo'] = False
            print(f"🗑️ Unloaded YOLO model")
        
        elif model_name == 'sam' and self.sam_predictor is not None:
            del self.sam_predictor
            self.sam_predictor = None
            self.loaded_models['sam'] = False
            print(f"🗑️ Unloaded SAM model")
        
        elif model_name == 'sdxl' and self.sdxl_pipeline is not None:
            del self.sdxl_pipeline
            self.sdxl_pipeline = None
            self.loaded_models['sdxl'] = False
            print(f"🗑️ Unloaded SDXL pipeline")
        
        elif model_name == 'depth':
            if self.depth_model is not None:
                del self.depth_model
                self.depth_model = None
            if self.depth_processor is not None:
                del self.depth_processor
                self.depth_processor = None
            self.loaded_models['depth'] = False
            print(f"🗑️ Unloaded depth model")
        
        # Force garbage collection
        gc.collect()
        if self.config.device == "cuda":
            torch.cuda.empty_cache()
    
    def unload_all_models(self):
        """Unload all models to free memory"""
        for model_name in list(self.loaded_models.keys()):
            self.unload_model(model_name)
    
    def get_memory_info(self) -> Dict[str, Any]:
        """Get current memory usage information"""
        info = {
            'device': self.config.device,
            'loaded_models': self.loaded_models.copy()
        }
        
        if self.config.device == "cuda":
            info.update({
                'gpu_memory_allocated': torch.cuda.memory_allocated() / 1024**3,  # GB
                'gpu_memory_reserved': torch.cuda.memory_reserved() / 1024**3,    # GB
                'gpu_memory_free': (torch.cuda.get_device_properties(0).total_memory - torch.cuda.memory_reserved()) / 1024**3,  # GB
                'gpu_name': torch.cuda.get_device_name(0)
            })
        
        return info
    
    def save_config(self, config_path: str = "model_manager_config.json"):
        """Save current configuration to file"""
        config_data = {
            'model_config': {
                'device': self.config.device,
                'torch_dtype': str(self.config.torch_dtype),
                'use_half_precision': self.config.use_half_precision,
                'enable_cache': self.config.enable_cache,
                'max_memory_usage': self.config.max_memory_usage
            },
            'model_paths': {
                'yolo_model_path': self.paths.yolo_model_path,
                'sam_checkpoint': self.paths.sam_checkpoint,
                'sdxl_base_path': self.paths.sdxl_base_path,
                'cache_dir': self.paths.cache_dir
            },
            'loaded_models': self.loaded_models
        }
        
        with open(config_path, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        print(f"✅ Configuration saved to {config_path}")
    
    def load_config(self, config_path: str = "model_manager_config.json"):
        """Load configuration from file"""
        if not os.path.exists(config_path):
            print(f"⚠️ Config file not found: {config_path}")
            return
        
        with open(config_path, 'r') as f:
            config_data = json.load(f)
        
        # Update configuration
        if 'model_config' in config_data:
            for key, value in config_data['model_config'].items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
        
        if 'model_paths' in config_data:
            for key, value in config_data['model_paths'].items():
                if hasattr(self.paths, key):
                    setattr(self.paths, key, value)
        
        print(f"✅ Configuration loaded from {config_path}")

def create_model_manager() -> EnhancedModelManager:
    """Factory function to create a configured model manager"""
    # Create configuration
    config = ModelConfig()
    paths = ModelPaths()
    
    # Create manager
    manager = EnhancedModelManager(config=config, paths=paths)
    
    return manager

# Global instance for easy access
_model_manager: Optional[EnhancedModelManager] = None

def get_model_manager() -> EnhancedModelManager:
    """Get or create global model manager instance"""
    global _model_manager
    if _model_manager is None:
        _model_manager = create_model_manager()
    return _model_manager

if __name__ == "__main__":
    # Test the model manager
    print("🧪 Testing Enhanced Model Manager...")
    
    manager = create_model_manager()
    
    # Print memory info
    print("\n📊 Memory Information:")
    memory_info = manager.get_memory_info()
    for key, value in memory_info.items():
        print(f"   {key}: {value}")
    
    # Try loading models
    print("\n🔁 Loading models...")
    try:
        models = manager.load_all_models()
        print(f"✅ Loaded {len(models)} models")
    except Exception as e:
        print(f"❌ Error loading models: {e}")
    
    # Save configuration
    manager.save_config()
    
    print("\n✅ Model manager test completed!") 