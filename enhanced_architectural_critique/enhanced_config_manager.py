#!/usr/bin/env python3
"""
Enhanced Configuration Manager for Architectural Critique System
Provides comprehensive configuration for all analysis components
"""

import json
import os
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum
from pathlib import Path

class AnalysisMode(Enum):
    """Analysis modes for different architectural contexts"""
    INTERIOR = "interior"
    EXTERIOR = "exterior"
    SITE_PLAN = "site_plan"
    FLOOR_PLAN = "floor_plan"
    SECTION = "section"
    ELEVATION = "elevation"

class ModelType(Enum):
    """Types of AI models"""
    YOLO_V8 = "yolov8"
    YOLO_V9 = "yolov9"
    SAM_VIT_H = "sam_vit_h"
    SAM_VIT_L = "sam_vit_l"
    SAM_VIT_B = "sam_vit_b"

@dataclass
class ModelConfig:
    """Enhanced configuration for AI models"""
    # YOLO Configuration
    yolo_model_path: str = "yolov8n.pt"
    yolo_model_type: ModelType = ModelType.YOLO_V8
    confidence_threshold: float = 0.5
    nms_threshold: float = 0.4
    max_detections: int = 100
    
    # SAM Configuration
    sam_checkpoint: str = "sam_vit_h_4b8939.pth"
    sam_model_type: ModelType = ModelType.SAM_VIT_H
    sam_points_per_side: int = 32
    sam_pred_iou_thresh: float = 0.88
    sam_stability_score_thresh: float = 0.95
    
    # Device Configuration
    device: str = "auto"  # auto, cuda, cpu, mps
    use_half_precision: bool = True
    enable_tensorrt: bool = False
    
    # Performance Configuration
    batch_size: int = 1
    num_workers: int = 4
    enable_cache: bool = True
    cache_dir: str = "cache"

@dataclass
class AnalysisConfig:
    """Configuration for analysis parameters"""
    # Analysis Mode
    analysis_mode: AnalysisMode = AnalysisMode.INTERIOR
    
    # Spatial Analysis
    min_object_distance: float = 50.0  # pixels
    max_relationship_distance: float = 500.0  # pixels
    alignment_threshold: float = 15.0  # degrees
    density_threshold: float = 0.4
    
    # Object Analysis
    min_object_area: float = 100.0  # pixels
    max_object_area: float = 10000.0  # pixels
    aspect_ratio_threshold: float = 5.0
    
    # Compliance Analysis
    enable_compliance_checking: bool = True
    compliance_tolerance: float = 0.1
    
    # Performance Settings
    enable_parallel_processing: bool = True
    max_analysis_time: int = 300  # seconds

@dataclass
class CritiqueConfig:
    """Enhanced configuration for critique parameters"""
    # Severity Weights
    severity_weights: Dict[str, float] = field(default_factory=lambda: {
        'functional': 1.2,
        'aesthetic': 0.8,
        'technical': 1.0,
        'accessibility': 1.5,
        'sustainability': 0.9,
        'circulation': 1.3,
        'lighting': 1.1,
        'acoustics': 0.7,
        'thermal': 0.8
    })
    
    # Category Priorities
    category_priorities: List[str] = field(default_factory=lambda: [
        'accessibility',
        'circulation',
        'functional',
        'technical',
        'lighting',
        'aesthetic',
        'sustainability',
        'acoustics',
        'thermal'
    ])
    
    # Critique Generation
    max_critique_points: int = 15
    min_severity_threshold: int = 2
    enable_positive_feedback: bool = True
    enable_cost_estimation: bool = True
    
    # Scoring Configuration
    base_score: float = 8.5
    max_penalty: float = 7.0
    score_weights: Dict[str, float] = field(default_factory=lambda: {
        'circulation_efficiency': 0.15,
        'lighting_quality': 0.12,
        'accessibility_compliance': 0.18,
        'spatial_hierarchy': 0.10,
        'aesthetic_balance': 0.12,
        'functional_optimization': 0.13,
        'technical_compliance': 0.20
    })

@dataclass
class VisualizationConfig:
    """Enhanced configuration for visual feedback"""
    # Color Schemes
    colors: Dict[str, Tuple[int, int, int]] = field(default_factory=lambda: {
        'functional': (255, 0, 0),      # Red
        'aesthetic': (0, 255, 0),       # Green
        'technical': (0, 0, 255),       # Blue
        'accessibility': (255, 255, 0), # Yellow
        'sustainability': (255, 0, 255), # Magenta
        'circulation': (0, 255, 255),   # Cyan
        'lighting': (255, 165, 0),      # Orange
        'acoustics': (128, 0, 128),     # Purple
        'thermal': (255, 20, 147)       # Deep Pink
    })
    
    # Object Visualization
    object_colors: Dict[str, Tuple[int, int, int]] = field(default_factory=lambda: {
        'circulation': (0, 255, 0),    # Green
        'lighting': (255, 255, 0),     # Yellow
        'furniture': (0, 255, 255),    # Cyan
        'fixtures': (255, 0, 255),     # Magenta
        'structure': (255, 165, 0),    # Orange
        'accessibility': (0, 0, 255),  # Blue
        'unknown': (128, 128, 128)     # Gray
    })
    
    # Drawing Parameters
    font_size: float = 0.7
    line_thickness: int = 2
    marker_size: int = 15
    overlay_alpha: float = 0.3
    text_thickness: int = 2
    
    # Layout Configuration
    legend_position: str = "top-left"  # top-left, top-right, bottom-left, bottom-right
    metrics_panel_position: str = "top-right"
    enable_legend: bool = True
    enable_metrics_panel: bool = True
    
    # Output Configuration
    output_format: str = "jpg"  # jpg, png, pdf
    output_quality: int = 95
    enable_multiple_outputs: bool = True

@dataclass
class ArchitecturalStandards:
    """Comprehensive architectural design standards"""
    # Room Standards
    min_room_area: float = 9.0  # square meters
    min_room_width: float = 2.4  # meters
    min_room_height: float = 2.4  # meters
    
    # Circulation Standards
    min_corridor_width: float = 1.2  # meters
    min_door_width: float = 0.85  # meters
    min_door_height: float = 2.1  # meters
    max_corridor_length: float = 30.0  # meters
    
    # Lighting Standards
    min_window_to_floor_ratio: float = 0.1
    max_window_to_floor_ratio: float = 0.25
    min_window_height: float = 1.2  # meters
    optimal_window_placement: float = 0.6  # height ratio
    
    # Accessibility Standards
    accessibility_requirements: Dict[str, float] = field(default_factory=lambda: {
        'min_door_width': 0.85,  # meters
        'max_ramp_slope': 0.083,  # 1:12 ratio
        'min_turning_radius': 1.5,  # meters
        'max_threshold_height': 0.013,  # meters
        'min_clearance_height': 2.1,  # meters
        'min_grab_bar_height': 0.33,  # meters
        'max_grab_bar_height': 0.48  # meters
    })
    
    # Density Standards
    max_occupancy_density: float = 0.4
    min_personal_space: float = 2.0  # square meters per person
    max_room_occupancy: Dict[str, int] = field(default_factory=lambda: {
        'bedroom': 2,
        'living_room': 6,
        'kitchen': 3,
        'bathroom': 1,
        'office': 2
    })
    
    # Sustainability Standards
    sustainability_requirements: Dict[str, float] = field(default_factory=lambda: {
        'min_insulation_r_value': 3.5,  # m²·K/W
        'max_air_leakage': 0.6,  # air changes per hour
        'min_daylight_factor': 2.0,  # percentage
        'max_glazing_ratio': 0.4,  # percentage
        'min_thermal_mass': 200.0  # kg/m²
    })

@dataclass
class PerformanceConfig:
    """Configuration for system performance"""
    # Processing Settings
    enable_gpu_acceleration: bool = True
    enable_multi_threading: bool = True
    max_memory_usage: int = 8192  # MB
    enable_memory_optimization: bool = True
    
    # Caching Settings
    enable_result_caching: bool = True
    cache_expiry_hours: int = 24
    max_cache_size: int = 1024  # MB
    
    # Optimization Settings
    enable_model_quantization: bool = False
    enable_batch_processing: bool = True
    enable_async_processing: bool = True

@dataclass
class ReportingConfig:
    """Configuration for report generation"""
    # Report Content
    include_detailed_analysis: bool = True
    include_visual_annotations: bool = True
    include_compliance_summary: bool = True
    include_cost_estimates: bool = True
    include_improvement_priorities: bool = True
    
    # Report Format
    output_formats: List[str] = field(default_factory=lambda: ['json', 'pdf', 'html'])
    include_executive_summary: bool = True
    max_report_length: int = 50  # pages
    
    # Customization
    company_logo_path: Optional[str] = None
    custom_stylesheet_path: Optional[str] = None
    enable_custom_branding: bool = False

@dataclass
class EnhancedAppConfig:
    """Main enhanced application configuration"""
    models: ModelConfig = field(default_factory=ModelConfig)
    analysis: AnalysisConfig = field(default_factory=AnalysisConfig)
    critique: CritiqueConfig = field(default_factory=CritiqueConfig)
    visualization: VisualizationConfig = field(default_factory=VisualizationConfig)
    standards: ArchitecturalStandards = field(default_factory=ArchitecturalStandards)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    reporting: ReportingConfig = field(default_factory=ReportingConfig)
    
    # Metadata
    version: str = "2.0.0"
    last_updated: str = ""
    description: str = "Enhanced Architectural Critique System Configuration"

class EnhancedConfigManager:
    """Enhanced configuration manager with comprehensive features"""
    
    def __init__(self, config_path: str = "enhanced_config.json"):
        self.config_path = config_path
        self.config = self.load_config()
        self._validate_and_fix_config()
    
    def load_config(self) -> EnhancedAppConfig:
        """Load configuration from file or create default"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    config_dict = json.load(f)
                return self._dict_to_config(config_dict)
            except Exception as e:
                print(f"Error loading config: {e}, using defaults")
                return self._create_default_config()
        else:
            # Create default config
            config = self._create_default_config()
            self.save_config(config)
            return config
    
    def _create_default_config(self) -> EnhancedAppConfig:
        """Create default configuration with optimized settings"""
        config = EnhancedAppConfig()
        
        # Set last updated timestamp
        from datetime import datetime
        config.last_updated = datetime.now().isoformat()
        
        return config
    
    def save_config(self, config: EnhancedAppConfig = None):
        """Save configuration to file"""
        if config is None:
            config = self.config
        
        config_dict = self._config_to_dict(config)
        with open(self.config_path, 'w') as f:
            json.dump(config_dict, f, indent=2)
        
        print(f"Configuration saved to {self.config_path}")
    
    def _config_to_dict(self, config: EnhancedAppConfig) -> Dict:
        """Convert config object to dictionary"""
        config_dict = asdict(config)
        
        # Handle enum serialization
        config_dict['analysis']['analysis_mode'] = config.analysis.analysis_mode.value
        config_dict['models']['yolo_model_type'] = config.models.yolo_model_type.value
        config_dict['models']['sam_model_type'] = config.models.sam_model_type.value
        
        return config_dict
    
    def _dict_to_config(self, config_dict: Dict) -> EnhancedAppConfig:
        """Convert dictionary to config object"""
        # Handle enum deserialization
        if 'analysis' in config_dict and 'analysis_mode' in config_dict['analysis']:
            config_dict['analysis']['analysis_mode'] = AnalysisMode(
                config_dict['analysis']['analysis_mode']
            )
        
        if 'models' in config_dict:
            if 'yolo_model_type' in config_dict['models']:
                config_dict['models']['yolo_model_type'] = ModelType(
                    config_dict['models']['yolo_model_type']
                )
            if 'sam_model_type' in config_dict['models']:
                config_dict['models']['sam_model_type'] = ModelType(
                    config_dict['models']['sam_model_type']
                )
        
        return EnhancedAppConfig(**config_dict)
    
    def update_model_config(self, **kwargs):
        """Update model configuration"""
        for key, value in kwargs.items():
            if hasattr(self.config.models, key):
                setattr(self.config.models, key, value)
        self.save_config()
    
    def update_analysis_config(self, **kwargs):
        """Update analysis configuration"""
        for key, value in kwargs.items():
            if hasattr(self.config.analysis, key):
                setattr(self.config.analysis, key, value)
        self.save_config()
    
    def update_critique_config(self, **kwargs):
        """Update critique configuration"""
        for key, value in kwargs.items():
            if hasattr(self.config.critique, key):
                setattr(self.config.critique, key, value)
        self.save_config()
    
    def update_visualization_config(self, **kwargs):
        """Update visualization configuration"""
        for key, value in kwargs.items():
            if hasattr(self.config.visualization, key):
                setattr(self.config.visualization, key, value)
        self.save_config()
    
    def update_standards(self, **kwargs):
        """Update architectural standards"""
        for key, value in kwargs.items():
            if hasattr(self.config.standards, key):
                setattr(self.config.standards, key, value)
        self.save_config()
    
    def update_performance_config(self, **kwargs):
        """Update performance configuration"""
        for key, value in kwargs.items():
            if hasattr(self.config.performance, key):
                setattr(self.config.performance, key, value)
        self.save_config()
    
    def update_reporting_config(self, **kwargs):
        """Update reporting configuration"""
        for key, value in kwargs.items():
            if hasattr(self.config.reporting, key):
                setattr(self.config.reporting, key, value)
        self.save_config()
    
    def get_analysis_mode_config(self, mode: AnalysisMode) -> Dict[str, Any]:
        """Get configuration optimized for specific analysis mode"""
        mode_configs = {
            AnalysisMode.INTERIOR: {
                'confidence_threshold': 0.4,
                'min_object_area': 50.0,
                'max_critique_points': 12,
                'focus_categories': ['functional', 'aesthetic', 'accessibility']
            },
            AnalysisMode.EXTERIOR: {
                'confidence_threshold': 0.5,
                'min_object_area': 200.0,
                'max_critique_points': 8,
                'focus_categories': ['aesthetic', 'technical', 'sustainability']
            },
            AnalysisMode.SITE_PLAN: {
                'confidence_threshold': 0.6,
                'min_object_area': 500.0,
                'max_critique_points': 10,
                'focus_categories': ['circulation', 'sustainability', 'technical']
            },
            AnalysisMode.FLOOR_PLAN: {
                'confidence_threshold': 0.4,
                'min_object_area': 100.0,
                'max_critique_points': 15,
                'focus_categories': ['functional', 'circulation', 'accessibility']
            }
        }
        
        return mode_configs.get(mode, {})
    
    def apply_analysis_mode(self, mode: AnalysisMode):
        """Apply configuration optimized for specific analysis mode"""
        mode_config = self.get_analysis_mode_config(mode)
        
        if mode_config:
            self.config.analysis.analysis_mode = mode
            self.update_model_config(**{k: v for k, v in mode_config.items() 
                                       if hasattr(self.config.models, k)})
            self.update_analysis_config(**{k: v for k, v in mode_config.items() 
                                          if hasattr(self.config.analysis, k)})
            self.update_critique_config(**{k: v for k, v in mode_config.items() 
                                          if hasattr(self.config.critique, k)})
    
    def validate_config(self) -> List[str]:
        """Comprehensive configuration validation"""
        issues = []
        
        # Model validation
        if not os.path.exists(self.config.models.yolo_model_path):
            issues.append(f"YOLO model not found: {self.config.models.yolo_model_path}")
        
        if not os.path.exists(self.config.models.sam_checkpoint):
            issues.append(f"SAM checkpoint not found: {self.config.models.sam_checkpoint}")
        
        if not 0 <= self.config.models.confidence_threshold <= 1:
            issues.append("Confidence threshold must be between 0 and 1")
        
        # Analysis validation
        if self.config.analysis.min_object_distance < 0:
            issues.append("Minimum object distance must be positive")
        
        if self.config.analysis.density_threshold <= 0 or self.config.analysis.density_threshold > 1:
            issues.append("Density threshold must be between 0 and 1")
        
        # Critique validation
        if self.config.critique.max_critique_points <= 0:
            issues.append("Maximum critique points must be positive")
        
        if not 0 <= self.config.critique.base_score <= 10:
            issues.append("Base score must be between 0 and 10")
        
        # Visualization validation
        if not 0 <= self.config.visualization.overlay_alpha <= 1:
            issues.append("Overlay alpha must be between 0 and 1")
        
        if self.config.visualization.output_quality < 1 or self.config.visualization.output_quality > 100:
            issues.append("Output quality must be between 1 and 100")
        
        # Performance validation
        if self.config.performance.max_memory_usage <= 0:
            issues.append("Maximum memory usage must be positive")
        
        return issues
    
    def _validate_and_fix_config(self):
        """Validate and automatically fix common configuration issues"""
        issues = self.validate_config()
        
        if issues:
            print("Configuration issues found:")
            for issue in issues:
                print(f"  - {issue}")
            
            # Try to fix common issues
            self._fix_common_issues()
        else:
            print("Configuration is valid")
    
    def _fix_common_issues(self):
        """Fix common configuration issues automatically"""
        fixes_applied = []
        
        # Fix confidence threshold
        if not 0 <= self.config.models.confidence_threshold <= 1:
            self.config.models.confidence_threshold = 0.5
            fixes_applied.append("Set confidence threshold to 0.5")
        
        # Fix density threshold
        if self.config.analysis.density_threshold <= 0 or self.config.analysis.density_threshold > 1:
            self.config.analysis.density_threshold = 0.4
            fixes_applied.append("Set density threshold to 0.4")
        
        # Fix overlay alpha
        if not 0 <= self.config.visualization.overlay_alpha <= 1:
            self.config.visualization.overlay_alpha = 0.3
            fixes_applied.append("Set overlay alpha to 0.3")
        
        if fixes_applied:
            print("Applied automatic fixes:")
            for fix in fixes_applied:
                print(f"  - {fix}")
            self.save_config()
    
    def export_config_template(self, output_path: str = "config_template.json"):
        """Export a configuration template"""
        template_config = self._create_default_config()
        template_dict = self._config_to_dict(template_config)
        
        with open(output_path, 'w') as f:
            json.dump(template_dict, f, indent=2)
        
        print(f"Configuration template exported to {output_path}")
    
    def import_config(self, import_path: str):
        """Import configuration from file"""
        try:
            with open(import_path, 'r') as f:
                config_dict = json.load(f)
            
            imported_config = self._dict_to_config(config_dict)
            self.config = imported_config
            self.save_config()
            
            print(f"Configuration imported from {import_path}")
            
        except Exception as e:
            print(f"Error importing configuration: {e}")
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get a summary of current configuration"""
        return {
            'version': self.config.version,
            'analysis_mode': self.config.analysis.analysis_mode.value,
            'model_type': self.config.models.yolo_model_type.value,
            'confidence_threshold': self.config.models.confidence_threshold,
            'max_critique_points': self.config.critique.max_critique_points,
            'enable_gpu': self.config.performance.enable_gpu_acceleration,
            'last_updated': self.config.last_updated
        }

def create_optimized_config(analysis_mode: AnalysisMode = AnalysisMode.INTERIOR) -> EnhancedConfigManager:
    """Create an optimized configuration for specific analysis mode"""
    config_manager = EnhancedConfigManager()
    config_manager.apply_analysis_mode(analysis_mode)
    return config_manager

def main():
    """Example usage and configuration management"""
    # Create enhanced config manager
    config_manager = EnhancedConfigManager()
    
    # Apply interior analysis mode
    config_manager.apply_analysis_mode(AnalysisMode.INTERIOR)
    
    # Customize settings
    config_manager.update_model_config(
        confidence_threshold=0.4,
        device="cuda"
    )
    
    config_manager.update_critique_config(
        max_critique_points=12,
        enable_cost_estimation=True
    )
    
    # Validate configuration
    issues = config_manager.validate_config()
    if issues:
        print("Configuration issues found:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("Configuration is valid")
    
    # Print configuration summary
    summary = config_manager.get_config_summary()
    print("\nConfiguration Summary:")
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    # Export template
    config_manager.export_config_template()

if __name__ == "__main__":
    main() 