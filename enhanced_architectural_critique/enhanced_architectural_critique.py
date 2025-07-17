#!/usr/bin/env python3
"""
Enhanced Architectural Critique System
A comprehensive, multimodal approach to architectural design analysis and feedback
"""

import cv2
import numpy as np
from ultralytics import YOLO
import torch
from segment_anything import sam_model_registry, SamPredictor
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
import json
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Any
import os
from pathlib import Path
from enum import Enum
import math
from scipy.spatial.distance import cdist
from scipy.optimize import linear_sum_assignment

class CritiqueCategory(Enum):
    """Enumeration of critique categories"""
    FUNCTIONAL = "functional"
    AESTHETIC = "aesthetic"
    TECHNICAL = "technical"
    ACCESSIBILITY = "accessibility"
    SUSTAINABILITY = "sustainability"
    CIRCULATION = "circulation"
    LIGHTING = "lighting"
    ACOUSTICS = "acoustics"
    THERMAL = "thermal"

class SeverityLevel(Enum):
    """Enumeration of severity levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class DetectedObject:
    """Enhanced detected architectural element with detailed properties"""
    bbox: Tuple[int, int, int, int]  # x1, y1, x2, y2
    confidence: float
    class_name: str
    mask: Optional[np.ndarray] = None
    center: Optional[Tuple[int, int]] = None
    area: Optional[float] = None
    aspect_ratio: Optional[float] = None
    orientation: Optional[float] = None
    spatial_context: Dict[str, Any] = field(default_factory=dict)
    architectural_function: Optional[str] = None
    compliance_score: Optional[float] = None

@dataclass
class SpatialRelationship:
    """Represents spatial relationship between objects"""
    object1_id: int
    object2_id: int
    distance: float
    angle: float
    relationship_type: str  # 'adjacent', 'aligned', 'proportional', 'conflicting'
    strength: float  # 0-1 scale
    description: str

@dataclass
class CritiquePoint:
    """Enhanced critique observation with detailed analysis"""
    category: CritiqueCategory
    severity: SeverityLevel
    title: str
    description: str
    location: Tuple[int, int]
    affected_objects: List[int]
    improvement_suggestion: str
    color: Tuple[int, int, int] = (255, 0, 0)
    evidence: List[str] = field(default_factory=list)
    standards_reference: Optional[str] = None
    impact_score: float = 0.0
    cost_estimate: Optional[str] = None
    priority: int = 1

@dataclass
class DesignMetrics:
    """Comprehensive design metrics"""
    circulation_efficiency: float = 0.0
    lighting_quality: float = 0.0
    spatial_hierarchy: float = 0.0
    accessibility_compliance: float = 0.0
    sustainability_score: float = 0.0
    aesthetic_balance: float = 0.0
    functional_optimization: float = 0.0
    technical_compliance: float = 0.0

class EnhancedArchitecturalCritiqueApp:
    """
    Enhanced architectural critique application with multimodal analysis
    """
    
    def __init__(self, yolo_model_path: str = "yolov8n.pt", 
                 sam_checkpoint: str = "sam_vit_h_4b8939.pth",
                 config_path: str = "config.json"):
        """
        Initialize the enhanced critique app
        
        Args:
            yolo_model_path: Path to YOLO model
            sam_checkpoint: Path to SAM model checkpoint
            config_path: Path to configuration file
        """
        self.yolo_model = YOLO(yolo_model_path)
        self.sam_model = None
        self.sam_predictor = None
        self.current_image = None
        self.detected_objects = []
        self.critique_points = []
        self.spatial_relationships = []
        self.design_metrics = DesignMetrics()
        
        # Load SAM model
        self._load_sam_model(sam_checkpoint)
        
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Enhanced architectural element mappings
        self.architectural_classes = {
            'door': {'function': 'circulation', 'priority': 1, 'min_area': 1.5},
            'window': {'function': 'lighting', 'priority': 2, 'min_area': 1.0},
            'chair': {'function': 'furniture', 'priority': 3, 'min_area': 0.5},
            'table': {'function': 'furniture', 'priority': 3, 'min_area': 1.0},
            'bed': {'function': 'furniture', 'priority': 3, 'min_area': 4.0},
            'sofa': {'function': 'furniture', 'priority': 3, 'min_area': 2.0},
            'toilet': {'function': 'fixtures', 'priority': 2, 'min_area': 1.5},
            'sink': {'function': 'fixtures', 'priority': 2, 'min_area': 0.5},
            'stairs': {'function': 'circulation', 'priority': 1, 'min_area': 2.0},
            'column': {'function': 'structure', 'priority': 1, 'min_area': 0.5},
            'wall': {'function': 'structure', 'priority': 1, 'min_area': 1.0},
            'ramp': {'function': 'accessibility', 'priority': 1, 'min_area': 3.0},
            'elevator': {'function': 'accessibility', 'priority': 1, 'min_area': 4.0}
        }
        
        # Critique categories with enhanced colors and weights
        self.critique_categories = {
            CritiqueCategory.FUNCTIONAL: {'color': (255, 0, 0), 'weight': 1.2},
            CritiqueCategory.AESTHETIC: {'color': (0, 255, 0), 'weight': 0.8},
            CritiqueCategory.TECHNICAL: {'color': (0, 0, 255), 'weight': 1.0},
            CritiqueCategory.ACCESSIBILITY: {'color': (255, 255, 0), 'weight': 1.5},
            CritiqueCategory.SUSTAINABILITY: {'color': (255, 0, 255), 'weight': 0.9},
            CritiqueCategory.CIRCULATION: {'color': (0, 255, 255), 'weight': 1.3},
            CritiqueCategory.LIGHTING: {'color': (255, 165, 0), 'weight': 1.1},
            CritiqueCategory.ACOUSTICS: {'color': (128, 0, 128), 'weight': 0.7},
            CritiqueCategory.THERMAL: {'color': (255, 20, 147), 'weight': 0.8}
        }
        
        # Architectural standards
        self.standards = {
            'min_room_area': 9.0,  # square meters
            'min_corridor_width': 1.2,  # meters
            'min_door_width': 0.85,  # meters
            'min_window_to_floor_ratio': 0.1,
            'max_occupancy_density': 0.4,
            'min_turning_radius': 1.5,  # meters for accessibility
            'max_ramp_slope': 0.083,  # 1:12 ratio
            'min_ceiling_height': 2.4,  # meters
            'optimal_window_placement': 0.6  # height ratio
        }
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from file"""
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
        return {}
    
    def _load_sam_model(self, checkpoint_path: str):
        """Load SAM model for segmentation"""
        try:
            model_type = "vit_h"
            sam = sam_model_registry[model_type](checkpoint=checkpoint_path)
            sam.to(device="cuda" if torch.cuda.is_available() else "cpu")
            self.sam_predictor = SamPredictor(sam)
            print("✓ SAM model loaded successfully")
        except Exception as e:
            print(f"⚠️ Warning: Could not load SAM model: {e}")
            print("SAM functionality will be disabled")
    
    def load_image(self, image_path: str) -> np.ndarray:
        """Load and preprocess image with enhanced preprocessing"""
        self.current_image = cv2.imread(image_path)
        if self.current_image is None:
            raise ValueError(f"Could not load image from {image_path}")
        
        # Enhanced preprocessing
        self.current_image = self._preprocess_image(self.current_image)
        
        # Set image for SAM if available
        if self.sam_predictor:
            rgb_image = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2RGB)
            self.sam_predictor.set_image(rgb_image)
        
        return self.current_image
    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Enhanced image preprocessing for better detection"""
        # Convert to RGB for better processing
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
        lab = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2LAB)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        lab[:,:,0] = clahe.apply(lab[:,:,0])
        enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
        
        # Convert back to BGR for OpenCV compatibility
        return cv2.cvtColor(enhanced, cv2.COLOR_RGB2BGR)
    
    def detect_objects(self, confidence_threshold: float = 0.5) -> List[DetectedObject]:
        """Enhanced object detection with detailed analysis"""
        if self.current_image is None:
            raise ValueError("No image loaded")
        
        results = self.yolo_model(self.current_image)
        self.detected_objects = []
        
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    # Extract box coordinates and confidence
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    confidence = box.conf[0].cpu().numpy()
                    class_id = int(box.cls[0].cpu().numpy())
                    class_name = self.yolo_model.names[class_id]
                    
                    if confidence >= confidence_threshold:
                        # Calculate enhanced properties
                        center = (int((x1 + x2) / 2), int((y1 + y2) / 2))
                        area = float((x2 - x1) * (y2 - y1))
                        aspect_ratio = float((x2 - x1) / (y2 - y1)) if (y2 - y1) > 0 else 1.0
                        orientation = math.atan2(y2 - y1, x2 - x1) * 180 / math.pi
                        
                        # Get architectural function
                        arch_info = self.architectural_classes.get(class_name, {})
                        architectural_function = arch_info.get('function', 'unknown')
                        
                        detected_obj = DetectedObject(
                            bbox=(int(x1), int(y1), int(x2), int(y2)),
                            confidence=float(confidence),
                            class_name=class_name,
                            center=center,
                            area=area,
                            aspect_ratio=aspect_ratio,
                            orientation=orientation,
                            architectural_function=architectural_function
                        )
                        
                        # Calculate compliance score
                        detected_obj.compliance_score = self._calculate_compliance_score(detected_obj)
                        
                        self.detected_objects.append(detected_obj)
        
        return self.detected_objects
    
    def _calculate_compliance_score(self, obj: DetectedObject) -> float:
        """Calculate compliance score based on architectural standards"""
        arch_info = self.architectural_classes.get(obj.class_name, {})
        min_area = arch_info.get('min_area', 1.0)
        
        # Convert pixel area to approximate square meters (assuming 1 pixel ≈ 0.01 sq meters)
        area_sqm = obj.area * 0.0001  # Rough conversion
        
        if area_sqm < min_area:
            return max(0.1, 1.0 - (min_area - area_sqm) / min_area)
        else:
            return min(1.0, 1.0 + (area_sqm - min_area) / min_area)
    
    def segment_objects(self) -> List[DetectedObject]:
        """Generate precise segmentation masks using SAM with enhanced processing"""
        if not self.sam_predictor:
            print("SAM not available, using bounding boxes only")
            return self.detected_objects
        
        for obj in self.detected_objects:
            try:
                # Use bounding box as prompt for SAM
                x1, y1, x2, y2 = obj.bbox
                input_box = np.array([x1, y1, x2, y2])
                
                masks, scores, logits = self.sam_predictor.predict(
                    point_coords=None,
                    point_labels=None,
                    box=input_box[None, :],
                    multimask_output=False,
                )
                
                # Use the best mask
                obj.mask = masks[0]
                
                # Calculate spatial context from mask
                obj.spatial_context = self._analyze_mask_context(obj.mask, obj.bbox)
                
            except Exception as e:
                print(f"Error segmenting object {obj.class_name}: {e}")
                
        return self.detected_objects
    
    def _analyze_mask_context(self, mask: np.ndarray, bbox: Tuple[int, int, int, int]) -> Dict[str, Any]:
        """Analyze spatial context from segmentation mask"""
        if mask is None:
            return {}
        
        # Calculate mask properties
        mask_area = np.sum(mask)
        mask_perimeter = self._calculate_mask_perimeter(mask)
        
        # Calculate compactness
        compactness = (4 * math.pi * mask_area) / (mask_perimeter ** 2) if mask_perimeter > 0 else 0
        
        return {
            'mask_area': float(mask_area),
            'mask_perimeter': float(mask_perimeter),
            'compactness': float(compactness),
            'shape_regularity': float(compactness)  # Higher compactness = more regular shape
        }
    
    def _calculate_mask_perimeter(self, mask: np.ndarray) -> float:
        """Calculate perimeter of binary mask"""
        # Use morphological operations to find edges
        kernel = np.ones((3,3), np.uint8)
        eroded = cv2.erode(mask.astype(np.uint8), kernel, iterations=1)
        dilated = cv2.dilate(mask.astype(np.uint8), kernel, iterations=1)
        edges = dilated - eroded
        return float(np.sum(edges))
    
    def analyze_spatial_relationships(self) -> Dict[str, Any]:
        """Comprehensive spatial relationship analysis"""
        if not self.detected_objects:
            return {}
        
        # Calculate all pairwise relationships
        self.spatial_relationships = self._calculate_spatial_relationships()
        
        # Analyze different aspects
        analysis = {
            'object_count': len(self.detected_objects),
            'density': self._calculate_density(),
            'circulation_analysis': self._analyze_circulation(),
            'lighting_analysis': self._analyze_lighting(),
            'accessibility_analysis': self._analyze_accessibility(),
            'spatial_hierarchy': self._analyze_spatial_hierarchy(),
            'functional_grouping': self._analyze_functional_grouping(),
            'proportional_analysis': self._analyze_proportions(),
            'alignment_analysis': self._analyze_alignments()
        }
        
        # Calculate design metrics
        self.design_metrics = self._calculate_design_metrics(analysis)
        
        return analysis
    
    def _calculate_density(self) -> float:
        """Calculate spatial density of objects with enhanced metrics"""
        if not self.current_image.size:
            return 0.0
        
        total_area = sum(obj.area for obj in self.detected_objects if obj.area)
        image_area = self.current_image.shape[0] * self.current_image.shape[1]
        density = total_area / image_area if image_area > 0 else 0.0
        
        # Normalize density (0-1 scale)
        return min(1.0, density / 0.5)  # 0.5 is considered high density
    
    def _analyze_circulation(self) -> Dict[str, Any]:
        """Enhanced circulation analysis"""
        doors = [obj for obj in self.detected_objects if obj.class_name == 'door']
        stairs = [obj for obj in self.detected_objects if obj.class_name == 'stairs']
        ramps = [obj for obj in self.detected_objects if obj.class_name == 'ramp']
        
        circulation_score = 8.0
        issues = []
        recommendations = []
        
        # Analyze door distribution
        if len(doors) == 0:
            issues.append("No doors detected - circulation may be unclear")
            circulation_score -= 3.0
            recommendations.append("Add doors to establish clear circulation paths")
        elif len(doors) == 1:
            issues.append("Single door may create circulation bottleneck")
            circulation_score -= 1.0
            recommendations.append("Consider adding secondary doors for better flow")
        elif len(doors) >= 3:
            circulation_score += 1.0
        
        # Analyze accessibility
        if len(ramps) == 0 and len(stairs) > 0:
            issues.append("Stairs without ramps may create accessibility issues")
            circulation_score -= 2.0
            recommendations.append("Add ramps or elevators for accessibility compliance")
        
        # Analyze circulation efficiency
        if len(doors) > 1:
            efficiency = self._calculate_circulation_efficiency(doors)
            circulation_score += efficiency * 2.0
        
        return {
            'score': max(1.0, min(10.0, circulation_score)),
            'door_count': len(doors),
            'stair_count': len(stairs),
            'ramp_count': len(ramps),
            'issues': issues,
            'recommendations': recommendations,
            'efficiency': self._calculate_circulation_efficiency(doors) if len(doors) > 1 else 0.0
        }
    
    def _calculate_circulation_efficiency(self, doors: List[DetectedObject]) -> float:
        """Calculate circulation efficiency based on door placement"""
        if len(doors) < 2:
            return 0.0
        
        # Calculate distances between doors
        door_centers = [door.center for door in doors]
        distances = []
        
        for i in range(len(door_centers)):
            for j in range(i+1, len(door_centers)):
                dist = math.sqrt(
                    (door_centers[i][0] - door_centers[j][0])**2 + 
                    (door_centers[i][1] - door_centers[j][1])**2
                )
                distances.append(dist)
        
        # Optimal efficiency: doors should be well-distributed but not too far apart
        avg_distance = np.mean(distances) if distances else 0
        std_distance = np.std(distances) if distances else 0
        
        # Efficiency score based on distribution
        efficiency = 1.0 - (std_distance / avg_distance) if avg_distance > 0 else 0.0
        return max(0.0, min(1.0, efficiency))
    
    def _analyze_lighting(self) -> Dict[str, Any]:
        """Enhanced lighting analysis"""
        windows = [obj for obj in self.detected_objects if obj.class_name == 'window']
        
        lighting_score = 5.0
        issues = []
        recommendations = []
        
        # Analyze window quantity
        if len(windows) == 0:
            issues.append("No windows detected - natural lighting may be insufficient")
            lighting_score = 2.0
            recommendations.append("Add windows for natural lighting")
        elif len(windows) >= 3:
            lighting_score = 9.0
        else:
            lighting_score = 6.0 + len(windows)
        
        # Analyze window placement
        if len(windows) > 0:
            placement_score = self._analyze_window_placement(windows)
            lighting_score += placement_score
        
        # Analyze window-to-floor ratio
        total_window_area = sum(win.area for win in windows)
        image_area = self.current_image.shape[0] * self.current_image.shape[1]
        window_ratio = total_window_area / image_area if image_area > 0 else 0
        
        if window_ratio < 0.05:
            issues.append("Window-to-floor ratio is below recommended standards")
            lighting_score -= 1.0
            recommendations.append("Increase window area for better natural lighting")
        
        return {
            'score': max(1.0, min(10.0, lighting_score)),
            'window_count': len(windows),
            'window_ratio': window_ratio,
            'placement_score': self._analyze_window_placement(windows) if windows else 0.0,
            'issues': issues,
            'recommendations': recommendations
        }
    
    def _analyze_window_placement(self, windows: List[DetectedObject]) -> float:
        """Analyze window placement for optimal lighting"""
        if not windows:
            return 0.0
        
        # Check if windows are distributed across the space
        window_centers = [win.center for win in windows]
        
        # Calculate distribution score
        x_coords = [center[0] for center in window_centers]
        y_coords = [center[1] for center in window_centers]
        
        x_std = np.std(x_coords) / self.current_image.shape[1]  # Normalized
        y_std = np.std(y_coords) / self.current_image.shape[0]  # Normalized
        
        # Higher standard deviation = better distribution
        distribution_score = (x_std + y_std) / 2.0
        
        return min(1.0, distribution_score * 2.0)  # Scale to 0-1
    
    def _analyze_accessibility(self) -> Dict[str, Any]:
        """Enhanced accessibility analysis"""
        stairs = [obj for obj in self.detected_objects if obj.class_name == 'stairs']
        doors = [obj for obj in self.detected_objects if obj.class_name == 'door']
        ramps = [obj for obj in self.detected_objects if obj.class_name == 'ramp']
        elevators = [obj for obj in self.detected_objects if obj.class_name == 'elevator']
        
        accessibility_score = 8.0
        issues = []
        recommendations = []
        
        # Check for accessibility alternatives
        if len(stairs) > 0 and len(ramps) == 0 and len(elevators) == 0:
            issues.append("Stairs without accessibility alternatives")
            accessibility_score -= 3.0
            recommendations.append("Add ramps or elevators for accessibility compliance")
        
        # Check door widths (approximate)
        for door in doors:
            door_width = door.bbox[2] - door.bbox[0]
            # Convert pixels to approximate meters (assuming 1 pixel ≈ 0.01 meters)
            door_width_m = door_width * 0.01
            if door_width_m < self.standards['min_door_width']:
                issues.append(f"Door width ({door_width_m:.2f}m) below accessibility standards")
                accessibility_score -= 1.0
                recommendations.append("Increase door width to meet accessibility standards")
        
        # Check for turning spaces
        turning_space_score = self._analyze_turning_spaces()
        accessibility_score += turning_space_score
        
        return {
            'score': max(1.0, min(10.0, accessibility_score)),
            'stair_count': len(stairs),
            'ramp_count': len(ramps),
            'elevator_count': len(elevators),
            'turning_space_score': turning_space_score,
            'issues': issues,
            'recommendations': recommendations
        }
    
    def _analyze_turning_spaces(self) -> float:
        """Analyze availability of turning spaces for accessibility"""
        # Look for open areas that could serve as turning spaces
        furniture = [obj for obj in self.detected_objects if obj.architectural_function == 'furniture']
        
        if not furniture:
            return 1.0  # No furniture means plenty of turning space
        
        # Calculate open areas
        total_furniture_area = sum(f.area for f in furniture)
        image_area = self.current_image.shape[0] * self.current_image.shape[1]
        open_area_ratio = 1.0 - (total_furniture_area / image_area)
        
        # Minimum 60% open area for good accessibility
        if open_area_ratio >= 0.6:
            return 1.0
        elif open_area_ratio >= 0.4:
            return 0.5
        else:
            return 0.0
    
    def _analyze_spatial_hierarchy(self) -> Dict[str, Any]:
        """Analyze spatial hierarchy and organization"""
        # Group objects by function
        function_groups = {}
        for obj in self.detected_objects:
            func = obj.architectural_function
            if func not in function_groups:
                function_groups[func] = []
            function_groups[func].append(obj)
        
        hierarchy_score = 5.0
        issues = []
        
        # Check for balanced distribution
        group_sizes = [len(group) for group in function_groups.values()]
        if group_sizes:
            size_variance = np.var(group_sizes)
            if size_variance > 2.0:  # High variance indicates imbalance
                issues.append("Unbalanced distribution of functional elements")
                hierarchy_score -= 1.0
        
        # Check for clear functional zones
        if len(function_groups) >= 3:
            hierarchy_score += 1.0
        elif len(function_groups) <= 1:
            issues.append("Limited functional diversity")
            hierarchy_score -= 1.0
        
        return {
            'score': max(1.0, min(10.0, hierarchy_score)),
            'functional_groups': len(function_groups),
            'group_distribution': group_sizes,
            'issues': issues
        }
    
    def _analyze_functional_grouping(self) -> Dict[str, Any]:
        """Analyze how well objects are grouped by function"""
        # Calculate clustering of objects by function
        function_clusters = {}
        
        for obj in self.detected_objects:
            func = obj.architectural_function
            if func not in function_clusters:
                function_clusters[func] = []
            function_clusters[func].append(obj.center)
        
        grouping_score = 5.0
        
        for func, centers in function_clusters.items():
            if len(centers) > 1:
                # Calculate average distance between objects of same function
                distances = []
                for i in range(len(centers)):
                    for j in range(i+1, len(centers)):
                        dist = math.sqrt(
                            (centers[i][0] - centers[j][0])**2 + 
                            (centers[i][1] - centers[j][1])**2
                        )
                        distances.append(dist)
                
                avg_distance = np.mean(distances) if distances else 0
                # Lower average distance = better grouping
                if avg_distance < 100:  # pixels
                    grouping_score += 0.5
                elif avg_distance > 300:  # pixels
                    grouping_score -= 0.5
        
        return {
            'score': max(1.0, min(10.0, grouping_score)),
            'function_clusters': len(function_clusters)
        }
    
    def _analyze_proportions(self) -> Dict[str, Any]:
        """Analyze proportional relationships"""
        proportion_score = 5.0
        issues = []
        
        # Analyze aspect ratios
        aspect_ratios = [obj.aspect_ratio for obj in self.detected_objects if obj.aspect_ratio]
        
        if aspect_ratios:
            # Check for extreme aspect ratios
            extreme_ratios = [r for r in aspect_ratios if r > 3.0 or r < 0.33]
            if extreme_ratios:
                issues.append(f"Found {len(extreme_ratios)} objects with extreme proportions")
                proportion_score -= len(extreme_ratios) * 0.5
        
        # Analyze size relationships
        areas = [obj.area for obj in self.detected_objects if obj.area]
        if len(areas) > 1:
            area_variance = np.var(areas)
            if area_variance > np.mean(areas) * 2:  # High variance
                issues.append("Significant size variation may affect visual balance")
                proportion_score -= 1.0
        
        return {
            'score': max(1.0, min(10.0, proportion_score)),
            'aspect_ratios': aspect_ratios,
            'issues': issues
        }
    
    def _analyze_alignments(self) -> Dict[str, Any]:
        """Analyze alignment patterns"""
        alignment_score = 5.0
        aligned_groups = 0
        
        # Find aligned objects
        for i, obj1 in enumerate(self.detected_objects):
            for obj2 in self.detected_objects[i+1:]:
                # Check horizontal alignment
                if abs(obj1.center[1] - obj2.center[1]) < 20:  # pixels
                    aligned_groups += 1
                
                # Check vertical alignment
                if abs(obj1.center[0] - obj2.center[0]) < 20:  # pixels
                    aligned_groups += 1
        
        # Reward good alignment
        if aligned_groups >= 3:
            alignment_score += 2.0
        elif aligned_groups >= 1:
            alignment_score += 1.0
        
        return {
            'score': max(1.0, min(10.0, alignment_score)),
            'aligned_groups': aligned_groups
        }
    
    def _calculate_design_metrics(self, analysis: Dict[str, Any]) -> DesignMetrics:
        """Calculate comprehensive design metrics"""
        metrics = DesignMetrics()
        
        # Circulation efficiency
        circulation = analysis.get('circulation_analysis', {})
        metrics.circulation_efficiency = circulation.get('score', 5.0) / 10.0
        
        # Lighting quality
        lighting = analysis.get('lighting_analysis', {})
        metrics.lighting_quality = lighting.get('score', 5.0) / 10.0
        
        # Spatial hierarchy
        hierarchy = analysis.get('spatial_hierarchy', {})
        metrics.spatial_hierarchy = hierarchy.get('score', 5.0) / 10.0
        
        # Accessibility compliance
        accessibility = analysis.get('accessibility_analysis', {})
        metrics.accessibility_compliance = accessibility.get('score', 5.0) / 10.0
        
        # Sustainability score (based on lighting and density)
        density = analysis.get('density', 0.5)
        metrics.sustainability_score = (1.0 - density) * 0.5 + lighting.get('score', 5.0) / 10.0 * 0.5
        
        # Aesthetic balance (based on proportions and alignments)
        proportions = analysis.get('proportional_analysis', {})
        alignments = analysis.get('alignment_analysis', {})
        metrics.aesthetic_balance = (
            proportions.get('score', 5.0) / 10.0 * 0.6 + 
            alignments.get('score', 5.0) / 10.0 * 0.4
        )
        
        # Functional optimization
        grouping = analysis.get('functional_grouping', {})
        metrics.functional_optimization = grouping.get('score', 5.0) / 10.0
        
        # Technical compliance (average of all technical aspects)
        technical_scores = [
            metrics.circulation_efficiency,
            metrics.lighting_quality,
            metrics.accessibility_compliance
        ]
        metrics.technical_compliance = np.mean(technical_scores)
        
        return metrics
    
    def generate_critique_points(self, spatial_analysis: Dict) -> List[CritiquePoint]:
        """Generate comprehensive critique points based on analysis"""
        self.critique_points = []
        
        # Circulation critique
        circulation = spatial_analysis.get('circulation_analysis', {})
        if circulation.get('score', 10) < 7:
            self._add_circulation_critique(circulation)
        
        # Lighting critique
        lighting = spatial_analysis.get('lighting_analysis', {})
        if lighting.get('score', 10) < 7:
            self._add_lighting_critique(lighting)
        
        # Accessibility critique
        accessibility = spatial_analysis.get('accessibility_analysis', {})
        if accessibility.get('score', 10) < 7:
            self._add_accessibility_critique(accessibility)
        
        # Spatial hierarchy critique
        hierarchy = spatial_analysis.get('spatial_hierarchy', {})
        if hierarchy.get('score', 10) < 6:
            self._add_hierarchy_critique(hierarchy)
        
        # Functional grouping critique
        grouping = spatial_analysis.get('functional_grouping', {})
        if grouping.get('score', 10) < 6:
            self._add_grouping_critique(grouping)
        
        # Proportional critique
        proportions = spatial_analysis.get('proportional_analysis', {})
        if proportions.get('score', 10) < 6:
            self._add_proportional_critique(proportions)
        
        # Density critique
        density = spatial_analysis.get('density', 0)
        if density > 0.4:
            self._add_density_critique(density)
        
        # Sort critique points by priority
        self.critique_points.sort(key=lambda x: x.priority, reverse=True)
        
        return self.critique_points
    
    def _add_circulation_critique(self, circulation: Dict):
        """Add circulation-related critique points"""
        severity = SeverityLevel.HIGH if circulation.get('score', 10) < 5 else SeverityLevel.MEDIUM
        
        critique = CritiquePoint(
            category=CritiqueCategory.CIRCULATION,
            severity=severity,
            title='Circulation Issues',
            description='; '.join(circulation.get('issues', ['Poor circulation design'])),
            location=(50, 50),
            affected_objects=[i for i, obj in enumerate(self.detected_objects) 
                            if obj.class_name in ['door', 'stairs', 'ramp']],
            improvement_suggestion='; '.join(circulation.get('recommendations', 
                            ['Review and improve circulation paths'])),
            color=self.critique_categories[CritiqueCategory.CIRCULATION]['color'],
            evidence=circulation.get('issues', []),
            standards_reference='Building Code Section 1005 - Means of Egress',
            impact_score=circulation.get('score', 5.0) / 10.0,
            priority=severity.value
        )
        
        self.critique_points.append(critique)
    
    def _add_lighting_critique(self, lighting: Dict):
        """Add lighting-related critique points"""
        severity = SeverityLevel.MEDIUM if lighting.get('score', 10) < 5 else SeverityLevel.LOW
        
        critique = CritiquePoint(
            category=CritiqueCategory.LIGHTING,
            severity=severity,
            title='Lighting Concerns',
            description='; '.join(lighting.get('issues', ['Insufficient natural lighting'])),
            location=(50, 100),
            affected_objects=[i for i, obj in enumerate(self.detected_objects) 
                            if obj.class_name == 'window'],
            improvement_suggestion='; '.join(lighting.get('recommendations', 
                            ['Improve natural lighting design'])),
            color=self.critique_categories[CritiqueCategory.LIGHTING]['color'],
            evidence=lighting.get('issues', []),
            standards_reference='ASHRAE 90.1 - Energy Standard for Buildings',
            impact_score=lighting.get('score', 5.0) / 10.0,
            priority=severity.value
        )
        
        self.critique_points.append(critique)
    
    def _add_accessibility_critique(self, accessibility: Dict):
        """Add accessibility-related critique points"""
        severity = SeverityLevel.CRITICAL if accessibility.get('score', 10) < 5 else SeverityLevel.HIGH
        
        critique = CritiquePoint(
            category=CritiqueCategory.ACCESSIBILITY,
            severity=severity,
            title='Accessibility Issues',
            description='; '.join(accessibility.get('issues', ['Accessibility compliance concerns'])),
            location=(50, 150),
            affected_objects=[i for i, obj in enumerate(self.detected_objects) 
                            if obj.class_name in ['stairs', 'door', 'ramp', 'elevator']],
            improvement_suggestion='; '.join(accessibility.get('recommendations', 
                            ['Review accessibility standards compliance'])),
            color=self.critique_categories[CritiqueCategory.ACCESSIBILITY]['color'],
            evidence=accessibility.get('issues', []),
            standards_reference='ADA Standards for Accessible Design',
            impact_score=accessibility.get('score', 5.0) / 10.0,
            priority=severity.value
        )
        
        self.critique_points.append(critique)
    
    def _add_hierarchy_critique(self, hierarchy: Dict):
        """Add spatial hierarchy critique points"""
        critique = CritiquePoint(
            category=CritiqueCategory.AESTHETIC,
            severity=SeverityLevel.MEDIUM,
            title='Spatial Hierarchy Issues',
            description='; '.join(hierarchy.get('issues', ['Poor spatial organization'])),
            location=(50, 200),
            affected_objects=list(range(len(self.detected_objects))),
            improvement_suggestion='Improve spatial organization and functional grouping',
            color=self.critique_categories[CritiqueCategory.AESTHETIC]['color'],
            evidence=hierarchy.get('issues', []),
            impact_score=hierarchy.get('score', 5.0) / 10.0,
            priority=2
        )
        
        self.critique_points.append(critique)
    
    def _add_grouping_critique(self, grouping: Dict):
        """Add functional grouping critique points"""
        critique = CritiquePoint(
            category=CritiqueCategory.FUNCTIONAL,
            severity=SeverityLevel.MEDIUM,
            title='Functional Grouping Issues',
            description='Poor functional organization of elements',
            location=(50, 250),
            affected_objects=list(range(len(self.detected_objects))),
            improvement_suggestion='Reorganize elements by function for better efficiency',
            color=self.critique_categories[CritiqueCategory.FUNCTIONAL]['color'],
            impact_score=grouping.get('score', 5.0) / 10.0,
            priority=2
        )
        
        self.critique_points.append(critique)
    
    def _add_proportional_critique(self, proportions: Dict):
        """Add proportional critique points"""
        critique = CritiquePoint(
            category=CritiqueCategory.AESTHETIC,
            severity=SeverityLevel.LOW,
            title='Proportional Issues',
            description='; '.join(proportions.get('issues', ['Poor proportional relationships'])),
            location=(50, 300),
            affected_objects=list(range(len(self.detected_objects))),
            improvement_suggestion='Review and adjust element proportions for better visual balance',
            color=self.critique_categories[CritiqueCategory.AESTHETIC]['color'],
            evidence=proportions.get('issues', []),
            impact_score=proportions.get('score', 5.0) / 10.0,
            priority=1
        )
        
        self.critique_points.append(critique)
    
    def _add_density_critique(self, density: float):
        """Add density-related critique points"""
        critique = CritiquePoint(
            category=CritiqueCategory.FUNCTIONAL,
            severity=SeverityLevel.MEDIUM,
            title='High Spatial Density',
            description=f'Space appears crowded (density: {density:.2f})',
            location=(50, 350),
            affected_objects=[i for i, obj in enumerate(self.detected_objects) 
                            if obj.architectural_function == 'furniture'],
            improvement_suggestion='Consider reducing furniture or increasing space size',
            color=self.critique_categories[CritiqueCategory.FUNCTIONAL]['color'],
            evidence=[f'Density ratio: {density:.2f}'],
            impact_score=density,
            priority=2
        )
        
        self.critique_points.append(critique) 
    
    def create_visual_feedback(self, output_path: str = "enhanced_critique_output.jpg"):
        """Create comprehensive annotated image with visual feedback"""
        if self.current_image is None:
            raise ValueError("No image loaded")
        
        # Create copy for annotation
        annotated_image = self.current_image.copy()
        
        # Draw detected objects with enhanced visualization
        for i, obj in enumerate(self.detected_objects):
            self._draw_object_annotation(annotated_image, obj, i)
        
        # Draw spatial relationships
        self._draw_spatial_relationships(annotated_image)
        
        # Draw critique points with enhanced visualization
        self._draw_critique_points(annotated_image)
        
        # Add comprehensive legend
        self._add_enhanced_legend(annotated_image)
        
        # Add design metrics summary
        self._add_metrics_summary(annotated_image)
        
        # Save annotated image
        cv2.imwrite(output_path, annotated_image)
        print(f"Enhanced annotated image saved to {output_path}")
        
        return annotated_image
    
    def _draw_object_annotation(self, image: np.ndarray, obj: DetectedObject, obj_id: int):
        """Draw enhanced object annotation"""
        x1, y1, x2, y2 = obj.bbox
        
        # Choose color based on architectural function
        color_map = {
            'circulation': (0, 255, 0),    # Green
            'lighting': (255, 255, 0),     # Yellow
            'furniture': (0, 255, 255),    # Cyan
            'fixtures': (255, 0, 255),     # Magenta
            'structure': (255, 165, 0),    # Orange
            'accessibility': (0, 0, 255),  # Blue
            'unknown': (128, 128, 128)     # Gray
        }
        
        color = color_map.get(obj.architectural_function, color_map['unknown'])
        
        # Draw bounding box
        cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
        
        # Draw object ID
        cv2.putText(image, f"{obj_id}", (x1, y1 - 25), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        # Draw label with confidence
        label = f"{obj.class_name}: {obj.confidence:.2f}"
        cv2.putText(image, label, (x1, y1 - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        # Draw compliance indicator
        if obj.compliance_score and obj.compliance_score < 0.7:
            cv2.circle(image, (x2 - 10, y1 + 10), 5, (0, 0, 255), -1)  # Red dot for non-compliance
        
        # Draw mask if available
        if obj.mask is not None:
            mask_overlay = np.zeros_like(image)
            mask_overlay[obj.mask] = [color[0], color[1], color[2]]
            image = cv2.addWeighted(image, 0.8, mask_overlay, 0.2, 0)
    
    def _draw_spatial_relationships(self, image: np.ndarray):
        """Draw spatial relationships between objects"""
        for rel in self.spatial_relationships:
            obj1 = self.detected_objects[rel.object1_id]
            obj2 = self.detected_objects[rel.object2_id]
            
            # Choose line color based on relationship type
            color_map = {
                'adjacent': (0, 255, 0),      # Green
                'aligned': (255, 255, 0),     # Yellow
                'proportional': (0, 255, 255), # Cyan
                'conflicting': (0, 0, 255),   # Red
                'neutral': (128, 128, 128)    # Gray
            }
            
            color = color_map.get(rel.relationship_type, color_map['neutral'])
            
            # Draw line between objects
            cv2.line(image, obj1.center, obj2.center, color, 1)
            
            # Draw relationship strength indicator
            mid_point = ((obj1.center[0] + obj2.center[0]) // 2, 
                        (obj1.center[1] + obj2.center[1]) // 2)
            radius = int(rel.strength * 5) + 1
            cv2.circle(image, mid_point, radius, color, -1)
    
    def _draw_critique_points(self, image: np.ndarray):
        """Draw enhanced critique points"""
        for i, critique in enumerate(self.critique_points):
            x, y = critique.location
            
            # Draw critique marker with severity indicator
            marker_size = critique.severity.value * 5 + 10
            cv2.circle(image, (x, y), marker_size, critique.color, -1)
            cv2.circle(image, (x, y), marker_size, (0, 0, 0), 2)
            
            # Draw severity number
            cv2.putText(image, str(critique.severity.value), 
                       (x - 8, y + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Draw title with background
            text_size = cv2.getTextSize(critique.title, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
            cv2.rectangle(image, (x + 25, y - 20), 
                         (x + 25 + text_size[0] + 10, y + 10), (255, 255, 255), -1)
            cv2.putText(image, critique.title, 
                       (x + 30, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, critique.color, 2)
            
            # Draw impact score
            impact_text = f"Impact: {critique.impact_score:.1f}"
            cv2.putText(image, impact_text, 
                       (x + 30, y + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (128, 128, 128), 1)
    
    def _add_enhanced_legend(self, image: np.ndarray):
        """Add comprehensive legend"""
        legend_y = 30
        legend_x = 10
        
        # Object types legend
        cv2.putText(image, "Object Types:", (legend_x, legend_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        legend_y += 25
        
        object_colors = {
            'Circulation': (0, 255, 0),
            'Lighting': (255, 255, 0),
            'Furniture': (0, 255, 255),
            'Fixtures': (255, 0, 255),
            'Structure': (255, 165, 0),
            'Accessibility': (0, 0, 255)
        }
        
        for obj_type, color in object_colors.items():
            cv2.circle(image, (legend_x + 10, legend_y - 5), 5, color, -1)
            cv2.putText(image, obj_type, (legend_x + 20, legend_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            legend_y += 20
        
        # Relationship types legend
        legend_y += 10
        cv2.putText(image, "Relationships:", (legend_x, legend_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        legend_y += 25
        
        rel_colors = {
            'Adjacent': (0, 255, 0),
            'Aligned': (255, 255, 0),
            'Proportional': (0, 255, 255),
            'Conflicting': (0, 0, 255)
        }
        
        for rel_type, color in rel_colors.items():
            cv2.line(image, (legend_x, legend_y), (legend_x + 20, legend_y), color, 2)
            cv2.putText(image, rel_type, (legend_x + 25, legend_y + 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            legend_y += 20
    
    def _add_metrics_summary(self, image: np.ndarray):
        """Add design metrics summary to image"""
        # Create metrics panel
        panel_width = 300
        panel_height = 200
        panel_x = image.shape[1] - panel_width - 10
        panel_y = 10
        
        # Draw panel background
        cv2.rectangle(image, (panel_x, panel_y), 
                     (panel_x + panel_width, panel_y + panel_height), 
                     (255, 255, 255), -1)
        cv2.rectangle(image, (panel_x, panel_y), 
                     (panel_x + panel_width, panel_y + panel_height), 
                     (0, 0, 0), 2)
        
        # Add title
        cv2.putText(image, "Design Metrics", (panel_x + 10, panel_y + 25), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        
        # Add metrics
        metrics_text = [
            f"Circulation: {self.design_metrics.circulation_efficiency:.2f}",
            f"Lighting: {self.design_metrics.lighting_quality:.2f}",
            f"Accessibility: {self.design_metrics.accessibility_compliance:.2f}",
            f"Spatial Hierarchy: {self.design_metrics.spatial_hierarchy:.2f}",
            f"Aesthetic Balance: {self.design_metrics.aesthetic_balance:.2f}",
            f"Overall Score: {self._calculate_overall_score():.1f}/10"
        ]
        
        for i, text in enumerate(metrics_text):
            y_pos = panel_y + 50 + i * 20
            cv2.putText(image, text, (panel_x + 10, y_pos), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
    
    def generate_report(self, output_path: str = "enhanced_critique_report.json"):
        """Generate comprehensive critique report"""
        report = {
            'analysis_metadata': {
                'timestamp': self._get_timestamp(),
                'image_dimensions': self.current_image.shape if self.current_image is not None else None,
                'total_objects': len(self.detected_objects),
                'total_critique_points': len(self.critique_points)
            },
            'detected_objects': [
                {
                    'id': i,
                    'class': obj.class_name,
                    'confidence': obj.confidence,
                    'bbox': obj.bbox,
                    'center': obj.center,
                    'area': obj.area,
                    'aspect_ratio': obj.aspect_ratio,
                    'orientation': obj.orientation,
                    'architectural_function': obj.architectural_function,
                    'compliance_score': obj.compliance_score,
                    'spatial_context': obj.spatial_context
                }
                for i, obj in enumerate(self.detected_objects)
            ],
            'spatial_relationships': [
                {
                    'object1_id': rel.object1_id,
                    'object2_id': rel.object2_id,
                    'distance': rel.distance,
                    'angle': rel.angle,
                    'relationship_type': rel.relationship_type,
                    'strength': rel.strength,
                    'description': rel.description
                }
                for rel in self.spatial_relationships
            ],
            'design_metrics': {
                'circulation_efficiency': self.design_metrics.circulation_efficiency,
                'lighting_quality': self.design_metrics.lighting_quality,
                'spatial_hierarchy': self.design_metrics.spatial_hierarchy,
                'accessibility_compliance': self.design_metrics.accessibility_compliance,
                'sustainability_score': self.design_metrics.sustainability_score,
                'aesthetic_balance': self.design_metrics.aesthetic_balance,
                'functional_optimization': self.design_metrics.functional_optimization,
                'technical_compliance': self.design_metrics.technical_compliance
            },
            'critique_points': [
                {
                    'category': cp.category.value,
                    'severity': cp.severity.value,
                    'title': cp.title,
                    'description': cp.description,
                    'location': cp.location,
                    'affected_objects': cp.affected_objects,
                    'improvement_suggestion': cp.improvement_suggestion,
                    'evidence': cp.evidence,
                    'standards_reference': cp.standards_reference,
                    'impact_score': cp.impact_score,
                    'priority': cp.priority
                }
                for cp in self.critique_points
            ],
            'overall_score': self._calculate_overall_score(),
            'recommendations': self._generate_recommendations(),
            'compliance_summary': self._generate_compliance_summary(),
            'improvement_priorities': self._generate_improvement_priorities()
        }
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"Enhanced report saved to {output_path}")
        return report
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _calculate_overall_score(self) -> float:
        """Calculate comprehensive overall design score"""
        if not self.critique_points:
            return 8.5
        
        # Base score from design metrics
        base_score = (
            self.design_metrics.circulation_efficiency * 0.15 +
            self.design_metrics.lighting_quality * 0.12 +
            self.design_metrics.accessibility_compliance * 0.18 +
            self.design_metrics.spatial_hierarchy * 0.10 +
            self.design_metrics.aesthetic_balance * 0.12 +
            self.design_metrics.functional_optimization * 0.13 +
            self.design_metrics.technical_compliance * 0.20
        ) * 10.0
        
        # Apply critique penalties
        total_penalty = 0.0
        for critique in self.critique_points:
            category_weight = self.critique_categories[critique.category]['weight']
            severity_penalty = critique.severity.value * 0.1 * category_weight
            total_penalty += severity_penalty
        
        final_score = max(1.0, base_score - total_penalty)
        return min(10.0, final_score)
    
    def _generate_recommendations(self) -> List[str]:
        """Generate prioritized recommendations"""
        recommendations = []
        
        # Sort critique points by priority and severity
        sorted_critiques = sorted(self.critique_points, 
                                key=lambda x: (x.priority, x.severity.value), reverse=True)
        
        for i, critique in enumerate(sorted_critiques[:5]):  # Top 5 priorities
            priority_level = "Critical" if critique.severity == SeverityLevel.CRITICAL else \
                           "High" if critique.severity == SeverityLevel.HIGH else \
                           "Medium" if critique.severity == SeverityLevel.MEDIUM else "Low"
            
            rec = f"{priority_level} Priority: {critique.improvement_suggestion}"
            if critique.standards_reference:
                rec += f" (Ref: {critique.standards_reference})"
            recommendations.append(rec)
        
        if not recommendations:
            recommendations.append("Excellent design! No major issues identified.")
        
        return recommendations
    
    def _generate_compliance_summary(self) -> Dict[str, Any]:
        """Generate compliance summary"""
        compliance_issues = []
        compliance_score = 0.0
        
        for obj in self.detected_objects:
            if obj.compliance_score and obj.compliance_score < 0.7:
                compliance_issues.append({
                    'object_class': obj.class_name,
                    'compliance_score': obj.compliance_score,
                    'issue': f"{obj.class_name} does not meet minimum size requirements"
                })
        
        if compliance_issues:
            compliance_score = np.mean([issue['compliance_score'] for issue in compliance_issues])
        else:
            compliance_score = 1.0
        
        return {
            'overall_compliance_score': compliance_score,
            'compliance_issues': compliance_issues,
            'standards_referenced': list(set([cp.standards_reference for cp in self.critique_points 
                                            if cp.standards_reference]))
        }
    
    def _generate_improvement_priorities(self) -> List[Dict[str, Any]]:
        """Generate improvement priorities with cost estimates"""
        priorities = []
        
        for critique in sorted(self.critique_points, 
                             key=lambda x: (x.priority, x.severity.value), reverse=True)[:3]:
            # Estimate improvement cost based on severity and category
            cost_estimate = self._estimate_improvement_cost(critique)
            
            priority = {
                'title': critique.title,
                'category': critique.category.value,
                'severity': critique.severity.value,
                'impact_score': critique.impact_score,
                'improvement_suggestion': critique.improvement_suggestion,
                'estimated_cost': cost_estimate,
                'implementation_difficulty': self._estimate_implementation_difficulty(critique)
            }
            priorities.append(priority)
        
        return priorities
    
    def _estimate_improvement_cost(self, critique: CritiquePoint) -> str:
        """Estimate improvement cost based on critique"""
        base_costs = {
            CritiqueCategory.ACCESSIBILITY: "High",
            CritiqueCategory.CIRCULATION: "Medium",
            CritiqueCategory.LIGHTING: "Medium",
            CritiqueCategory.FUNCTIONAL: "Low",
            CritiqueCategory.AESTHETIC: "Low",
            CritiqueCategory.TECHNICAL: "Medium",
            CritiqueCategory.SUSTAINABILITY: "High",
            CritiqueCategory.ACOUSTICS: "Medium",
            CritiqueCategory.THERMAL: "High"
        }
        
        base_cost = base_costs.get(critique.category, "Medium")
        
        # Adjust based on severity
        if critique.severity == SeverityLevel.CRITICAL:
            return f"{base_cost} to Very High"
        elif critique.severity == SeverityLevel.HIGH:
            return f"Medium to {base_cost}"
        else:
            return f"Low to {base_cost}"
    
    def _estimate_implementation_difficulty(self, critique: CritiquePoint) -> str:
        """Estimate implementation difficulty"""
        difficulties = {
            CritiqueCategory.ACCESSIBILITY: "High",
            CritiqueCategory.CIRCULATION: "Medium",
            CritiqueCategory.LIGHTING: "Medium",
            CritiqueCategory.FUNCTIONAL: "Low",
            CritiqueCategory.AESTHETIC: "Low",
            CritiqueCategory.TECHNICAL: "Medium",
            CritiqueCategory.SUSTAINABILITY: "High",
            CritiqueCategory.ACOUSTICS: "Medium",
            CritiqueCategory.THERMAL: "High"
        }
        
        return difficulties.get(critique.category, "Medium")

def main():
    """Example usage of the enhanced architectural critique app"""
    app = EnhancedArchitecturalCritiqueApp()
    
    # Load image
    image_path = "sample_architecture.jpg"  # Replace with your image path
    try:
        app.load_image(image_path)
        print(f"Image loaded successfully: {image_path}")
    except ValueError as e:
        print(f"Error loading image: {e}")
        return
    
    # Detect objects
    objects = app.detect_objects(confidence_threshold=0.3)
    print(f"Detected {len(objects)} objects")
    
    # Segment objects (if SAM is available)
    app.segment_objects()
    
    # Analyze spatial relationships
    analysis = app.analyze_spatial_relationships()
    print("Enhanced spatial analysis completed")
    
    # Generate critique points
    critiques = app.generate_critique_points(analysis)
    print(f"Generated {len(critiques)} critique points")
    
    # Create visual feedback
    app.create_visual_feedback("enhanced_annotated_output.jpg")
    
    # Generate comprehensive report
    report = app.generate_report("enhanced_critique_report.json")
    
    print(f"\nOverall Score: {report['overall_score']:.1f}/10")
    print(f"\nDesign Metrics:")
    for metric, value in report['design_metrics'].items():
        print(f"  {metric}: {value:.2f}")
    
    print(f"\nTop Recommendations:")
    for rec in report['recommendations']:
        print(f"- {rec}")
    
    print(f"\nImprovement Priorities:")
    for priority in report['improvement_priorities']:
        print(f"- {priority['title']}: {priority['estimated_cost']} cost, {priority['implementation_difficulty']} difficulty")

if __name__ == "__main__":
    main() 