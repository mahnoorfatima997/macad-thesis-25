#!/usr/bin/env python3
"""
Comprehensive Architectural Analysis Module
Provides detailed analysis across multiple categories including spatial, functional, technical, and aesthetic analysis
"""

import numpy as np
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass
from enum import Enum

class AnalysisCategory(Enum):
    """Analysis categories with severity levels"""
    FUNCTIONAL = "functional"      # Red - Critical usability issues
    AESTHETIC = "aesthetic"        # Green - Visual/design quality
    TECHNICAL = "technical"        # Blue - Technical/construction issues
    ACCESSIBILITY = "accessibility" # Yellow - Universal design issues
    SUSTAINABILITY = "sustainability" # Magenta - Environmental issues
    CIRCULATION = "circulation"    # Cyan - Movement/flow issues
    LIGHTING = "lighting"          # Orange - Natural/artificial lighting
    ACOUSTICS = "acoustics"        # Purple - Sound/acoustic issues
    THERMAL = "thermal"            # Pink - Thermal comfort issues

@dataclass
class AnalysisScore:
    """Analysis score with category and details"""
    category: AnalysisCategory
    score: float  # 0-100
    severity: str  # "low", "medium", "high", "critical"
    issues: List[str]
    recommendations: List[str]
    impact: str  # "low", "medium", "high"

class ComprehensiveArchitecturalAnalyzer:
    """Comprehensive architectural analysis across all categories"""
    
    def __init__(self):
        """Initialize the comprehensive analyzer"""
        self.architectural_classes = {
            # Structural Elements (0-11)
            0: "wall", 1: "courtyard", 2: "bedroom", 3: "bathroom", 4: "door",
            5: "living_room", 6: "dining_room", 7: "kitchen", 8: "toilet",
            9: "corridor", 10: "circulation_node", 11: "window",
            
            # Elevation Elements (12-30)
            12: "facade", 13: "roof", 14: "column", 15: "balcony", 16: "parapet",
            17: "railing", 18: "staircase", 19: "ground_line", 20: "elevation_marker",
            21: "arrow", 22: "text_label", 23: "axis", 24: "tree", 25: "human_figure",
            26: "sun_path", 27: "shading_device", 28: "material_texture",
            29: "dashed_line", 30: "north_arrow"
        }
    
    def analyze_architecture(self, yolo_detections: List[Dict], sam_segments: List[Dict], 
                           clip_blip_analysis: Dict) -> Dict[str, Any]:
        """
        Perform comprehensive architectural analysis
        
        Args:
            yolo_detections: List of YOLO detection results
            sam_segments: List of SAM segmentation results
            clip_blip_analysis: CLIP/BLIP analysis results
            
        Returns:
            dict: Comprehensive analysis results
        """
        analysis_results = {
            "spatial_analysis": self._perform_spatial_analysis(yolo_detections, sam_segments),
            "functional_analysis": self._perform_functional_analysis(yolo_detections, clip_blip_analysis),
            "technical_analysis": self._perform_technical_analysis(yolo_detections),
            "aesthetic_analysis": self._perform_aesthetic_analysis(clip_blip_analysis),
            "accessibility_analysis": self._perform_accessibility_analysis(yolo_detections),
            "sustainability_analysis": self._perform_sustainability_analysis(yolo_detections, clip_blip_analysis),
            "circulation_analysis": self._perform_circulation_analysis(yolo_detections),
            "lighting_analysis": self._perform_lighting_analysis(yolo_detections, clip_blip_analysis),
            "acoustics_analysis": self._perform_acoustics_analysis(yolo_detections),
            "thermal_analysis": self._perform_thermal_analysis(yolo_detections, clip_blip_analysis),
            "overall_assessment": {},
            "critical_issues": [],
            "recommendations": []
        }
        
        # Generate overall assessment
        analysis_results["overall_assessment"] = self._generate_overall_assessment(analysis_results)
        
        # Extract critical issues and recommendations
        analysis_results["critical_issues"] = self._extract_critical_issues(analysis_results)
        analysis_results["recommendations"] = self._extract_recommendations(analysis_results)
        
        return analysis_results
    
    def _perform_spatial_analysis(self, detections: List[Dict], segments: List[Dict]) -> Dict[str, Any]:
        """Perform spatial analysis including circulation efficiency, adjacency, density, and proportions"""
        analysis = {
            "circulation_efficiency": 0.0,
            "adjacency_analysis": {},
            "density_calculation": 0.0,
            "proportional_analysis": {},
            "spatial_relationships": {},
            "room_distribution": {},
            "issues": [],
            "recommendations": []
        }
        
        if not detections:
            analysis["issues"].append("No architectural elements detected")
            return analysis
        
        # Extract detailed information from detections
        element_types = [d["class_name"] for d in detections]
        element_areas = [d["area"] for d in detections]
        element_confidences = [d["confidence"] for d in detections]
        element_bboxes = [d["bbox"] for d in detections]
        
        # Calculate weighted scores based on confidence
        weighted_scores = {}
        for i, elem_type in enumerate(element_types):
            confidence = element_confidences[i]
            if elem_type not in weighted_scores:
                weighted_scores[elem_type] = []
            weighted_scores[elem_type].append(confidence)
        
        # Circulation Efficiency (0-100%) - Based on actual detected elements
        circulation_elements = ["door", "corridor", "circulation_node", "staircase"]
        circulation_detections = [d for d in detections if d["class_name"] in circulation_elements]
        
        if circulation_detections:
            # Calculate circulation efficiency based on confidence and area
            total_circulation_area = sum(d["area"] for d in circulation_detections)
            avg_circulation_confidence = np.mean([d["confidence"] for d in circulation_detections])
            
            # More sophisticated calculation
            circulation_efficiency = min(100, (len(circulation_detections) * 20 + 
                                             avg_circulation_confidence * 50 + 
                                             min(100, total_circulation_area / 10000)))
            analysis["circulation_efficiency"] = circulation_efficiency
            
            if circulation_efficiency < 60:
                analysis["issues"].append(f"Limited circulation elements detected (efficiency: {circulation_efficiency:.1f}%)")
                analysis["recommendations"].append("Consider adding more doors, corridors, or circulation nodes")
        else:
            analysis["issues"].append("No circulation elements detected")
            analysis["recommendations"].append("Add circulation elements for better space flow")
        
        # Advanced Adjacency Analysis
        adjacency_score = 0.0
        adjacency_details = {}
        
        # Kitchen-Dining adjacency (very good if both present)
        if "kitchen" in element_types and "dining_room" in element_types:
            kitchen_conf = np.mean([d["confidence"] for d in detections if d["class_name"] == "kitchen"])
            dining_conf = np.mean([d["confidence"] for d in detections if d["class_name"] == "dining_room"])
            adjacency_score += 30 * (kitchen_conf + dining_conf) / 2
            adjacency_details["kitchen_dining"] = {
                "present": True,
                "kitchen_confidence": kitchen_conf,
                "dining_confidence": dining_conf,
                "score": 30 * (kitchen_conf + dining_conf) / 2
            }
        
        # Bathroom accessibility
        if "bathroom" in element_types:
            bathroom_conf = np.mean([d["confidence"] for d in detections if d["class_name"] == "bathroom"])
            adjacency_score += 25 * bathroom_conf
            adjacency_details["bathroom_accessibility"] = {
                "present": True,
                "confidence": bathroom_conf,
                "score": 25 * bathroom_conf
            }
        
        # Corridor connectivity
        if "corridor" in element_types:
            corridor_conf = np.mean([d["confidence"] for d in detections if d["class_name"] == "corridor"])
            adjacency_score += 25 * corridor_conf
            adjacency_details["corridor_connectivity"] = {
                "present": True,
                "confidence": corridor_conf,
                "score": 25 * corridor_conf
            }
        
        analysis["adjacency_analysis"] = {
            "score": adjacency_score,
            "details": adjacency_details,
            "kitchen_dining": "kitchen" in element_types and "dining_room" in element_types,
            "bathroom_present": "bathroom" in element_types,
            "corridor_present": "corridor" in element_types
        }
        
        # Advanced Density Calculation
        if element_areas:
            total_area = sum(element_areas)
            avg_confidence = np.mean(element_confidences)
            
            # Density based on number of elements, their confidence, and area distribution
            density = (len(detections) * avg_confidence * 10) / max(1, total_area / 50000)
            analysis["density_calculation"] = min(100, density)
        
        # Sophisticated Proportional Analysis
        if element_areas:
            avg_area = np.mean(element_areas)
            std_area = np.std(element_areas)
            area_ratio = std_area / max(1, avg_area)
            
            # Room size distribution analysis
            room_sizes = {}
            for i, elem_type in enumerate(element_types):
                if elem_type not in room_sizes:
                    room_sizes[elem_type] = []
                room_sizes[elem_type].append(element_areas[i])
            
            size_analysis = {}
            for room_type, sizes in room_sizes.items():
                size_analysis[room_type] = {
                    "count": len(sizes),
                    "avg_size": np.mean(sizes),
                    "size_variation": np.std(sizes) / max(1, np.mean(sizes))
                }
            
            analysis["proportional_analysis"] = {
                "area_consistency": max(0, 100 - area_ratio * 100),
                "average_element_size": avg_area,
                "size_variation": area_ratio,
                "room_size_distribution": size_analysis
            }
            
            # Check for proportional issues
            if area_ratio > 0.8:
                analysis["issues"].append("High variation in room sizes - consider more consistent proportions")
                analysis["recommendations"].append("Standardize room sizes for better spatial harmony")
        
        # Spatial Relationships Analysis
        if len(element_bboxes) > 1:
            spatial_relationships = self._analyze_spatial_relationships(element_bboxes, element_types)
            analysis["spatial_relationships"] = spatial_relationships
        
        # Room Distribution Analysis
        room_distribution = {}
        for elem_type in element_types:
            room_distribution[elem_type] = room_distribution.get(elem_type, 0) + 1
        
        analysis["room_distribution"] = {
            "total_rooms": len(detections),
            "room_types": room_distribution,
            "functional_balance": self._calculate_functional_balance(room_distribution)
        }
        
        return analysis
    
    def _analyze_spatial_relationships(self, bboxes: List[List[int]], element_types: List[str]) -> Dict[str, Any]:
        """Analyze spatial relationships between detected elements"""
        relationships = {
            "proximity_analysis": {},
            "layout_pattern": "unknown",
            "spatial_efficiency": 0.0
        }
        
        if len(bboxes) < 2:
            return relationships
        
        # Calculate distances between elements
        distances = []
        for i in range(len(bboxes)):
            for j in range(i + 1, len(bboxes)):
                # Calculate center points
                center1 = [(bboxes[i][0] + bboxes[i][2]) / 2, (bboxes[i][1] + bboxes[i][3]) / 2]
                center2 = [(bboxes[j][0] + bboxes[j][2]) / 2, (bboxes[j][1] + bboxes[j][3]) / 2]
                
                # Euclidean distance
                distance = np.sqrt((center1[0] - center2[0])**2 + (center1[1] - center2[1])**2)
                distances.append(distance)
        
        if distances:
            avg_distance = np.mean(distances)
            relationships["proximity_analysis"] = {
                "average_distance": avg_distance,
                "distance_variation": np.std(distances),
                "closest_elements": min(distances),
                "farthest_elements": max(distances)
            }
            
            # Determine layout pattern
            if avg_distance < 200:
                relationships["layout_pattern"] = "compact"
            elif avg_distance < 400:
                relationships["layout_pattern"] = "moderate"
            else:
                relationships["layout_pattern"] = "spread_out"
        
        return relationships
    
    def _calculate_functional_balance(self, room_distribution: Dict[str, int]) -> float:
        """Calculate functional balance of room distribution"""
        functional_rooms = ["bedroom", "bathroom", "kitchen", "living_room", "dining_room"]
        total_functional = sum(room_distribution.get(room, 0) for room in functional_rooms)
        total_rooms = sum(room_distribution.values())
        
        if total_rooms == 0:
            return 0.0
        
        return (total_functional / total_rooms) * 100
    
    def _perform_functional_analysis(self, detections: List[Dict], clip_blip_analysis: Dict) -> Dict[str, Any]:
        """Perform functional analysis including room functionality, accessibility, lighting, and ventilation"""
        analysis = {
            "room_functionality": 0.0,
            "accessibility": 0.0,
            "lighting_quality": 0.0,
            "ventilation": 0.0,
            "functional_efficiency": 0.0,
            "space_utilization": {},
            "issues": [],
            "recommendations": []
        }
        
        if not detections:
            analysis["issues"].append("No functional elements detected")
            return analysis
        
        element_types = [d["class_name"] for d in detections]
        element_confidences = [d["confidence"] for d in detections]
        element_areas = [d["area"] for d in detections]
        
        # Advanced Room Functionality Analysis
        functional_rooms = ["bedroom", "bathroom", "kitchen", "living_room", "dining_room"]
        functional_detections = [d for d in detections if d["class_name"] in functional_rooms]
        
        if functional_detections:
            # Calculate weighted functionality score based on confidence and area
            total_functional_area = sum(d["area"] for d in functional_detections)
            avg_functional_confidence = np.mean([d["confidence"] for d in functional_detections])
            
            # More sophisticated calculation
            functionality_score = min(100, (len(functional_detections) * 15 + 
                                          avg_functional_confidence * 60 + 
                                          min(25, total_functional_area / 20000)))
            analysis["room_functionality"] = functionality_score
            
            # Analyze each functional room type
            room_analysis = {}
            for room_type in functional_rooms:
                room_detections = [d for d in detections if d["class_name"] == room_type]
                if room_detections:
                    room_analysis[room_type] = {
                        "count": len(room_detections),
                        "avg_confidence": np.mean([d["confidence"] for d in room_detections]),
                        "total_area": sum(d["area"] for d in room_detections),
                        "avg_area": np.mean([d["area"] for d in room_detections])
                    }
            
            analysis["space_utilization"] = room_analysis
        else:
            analysis["issues"].append("No functional rooms detected")
            analysis["recommendations"].append("Add functional spaces (bedrooms, bathrooms, kitchens)")
        
        # Advanced Accessibility Analysis
        accessibility_elements = ["door", "corridor", "circulation_node"]
        accessibility_detections = [d for d in detections if d["class_name"] in accessibility_elements]
        
        if accessibility_detections:
            accessibility_score = min(100, (len(accessibility_detections) * 20 + 
                                          np.mean([d["confidence"] for d in accessibility_detections]) * 50))
            analysis["accessibility"] = accessibility_score
        else:
            analysis["accessibility"] = 20  # Very poor accessibility
            analysis["issues"].append("No accessibility elements detected")
            analysis["recommendations"].append("Add doors, corridors, or circulation nodes")
        
        # Advanced Lighting Quality Analysis
        lighting_elements = ["window", "sun_path", "shading_device"]
        lighting_detections = [d for d in detections if d["class_name"] in lighting_elements]
        
        if lighting_detections:
            lighting_score = min(100, (len(lighting_detections) * 25 + 
                                     np.mean([d["confidence"] for d in lighting_detections]) * 60))
            analysis["lighting_quality"] = lighting_score
        else:
            analysis["lighting_quality"] = 15  # Very poor lighting
            analysis["issues"].append("No lighting elements detected")
            analysis["recommendations"].append("Add windows for natural lighting")
        
        # Advanced Ventilation Analysis
        ventilation_elements = ["window", "door", "corridor"]
        ventilation_detections = [d for d in detections if d["class_name"] in ventilation_elements]
        
        if ventilation_detections:
            ventilation_score = min(100, (len(ventilation_detections) * 15 + 
                                        np.mean([d["confidence"] for d in ventilation_detections]) * 70))
            analysis["ventilation"] = ventilation_score
        else:
            analysis["ventilation"] = 10  # Very poor ventilation
            analysis["issues"].append("No ventilation elements detected")
            analysis["recommendations"].append("Add windows and doors for ventilation")
        
        # Functional Efficiency (overall score)
        efficiency_scores = [
            analysis["room_functionality"],
            analysis["accessibility"],
            analysis["lighting_quality"],
            analysis["ventilation"]
        ]
        analysis["functional_efficiency"] = np.mean(efficiency_scores)
        
        # Generate specific recommendations based on detected elements
        if "kitchen" in element_types and "dining_room" in element_types:
            analysis["recommendations"].append("Good kitchen-dining room adjacency detected")
        
        if "bathroom" in element_types:
            bathroom_conf = np.mean([d["confidence"] for d in detections if d["class_name"] == "bathroom"])
            if bathroom_conf < 0.6:
                analysis["issues"].append("Bathroom detection confidence is low")
                analysis["recommendations"].append("Verify bathroom layout and accessibility")
        
        if "corridor" in element_types:
            corridor_conf = np.mean([d["confidence"] for d in detections if d["class_name"] == "corridor"])
            if corridor_conf < 0.5:
                analysis["issues"].append("Corridor detection confidence is low")
                analysis["recommendations"].append("Improve corridor definition and connectivity")
        
        return analysis
    
    def _perform_technical_analysis(self, detections: List[Dict]) -> Dict[str, Any]:
        """Perform technical analysis including structural integrity, code compliance, energy efficiency, and materials"""
        analysis = {
            "structural_integrity": 0.0,
            "code_compliance": 0.0,
            "energy_efficiency": 0.0,
            "material_analysis": {},
            "issues": [],
            "recommendations": []
        }
        
        element_types = [d["class_name"] for d in detections]
        
        # Structural Integrity
        structural_elements = ["wall", "column", "roof", "foundation"]
        structural_count = sum(1 for elem in element_types if elem in structural_elements)
        analysis["structural_integrity"] = min(100, (structural_count / max(1, len(element_types))) * 200)
        
        # Code Compliance (basic checks)
        compliance_score = 0
        if "door" in element_types:
            compliance_score += 25  # Egress requirements
        if "window" in element_types:
            compliance_score += 25  # Ventilation requirements
        if "corridor" in element_types:
            compliance_score += 25  # Circulation requirements
        if "bathroom" in element_types:
            compliance_score += 25  # Sanitation requirements
        
        analysis["code_compliance"] = compliance_score
        
        # Energy Efficiency
        efficiency_elements = ["window", "shading_device", "sun_path"]
        efficiency_count = sum(1 for elem in element_types if elem in efficiency_elements)
        analysis["energy_efficiency"] = min(100, (efficiency_count / max(1, len(element_types))) * 200)
        
        # Material Analysis
        material_elements = ["material_texture", "facade", "roof"]
        material_count = sum(1 for elem in element_types if elem in material_elements)
        analysis["material_analysis"] = {
            "material_diversity": min(100, (material_count / max(1, len(element_types))) * 200),
            "materials_detected": [elem for elem in element_types if elem in material_elements]
        }
        
        # Issues and recommendations
        if analysis["structural_integrity"] < 50:
            analysis["issues"].append("Insufficient structural elements")
            analysis["recommendations"].append("Ensure adequate structural support")
        
        if analysis["code_compliance"] < 75:
            analysis["issues"].append("Potential code compliance issues")
            analysis["recommendations"].append("Review building code requirements")
        
        return analysis
    
    def _perform_aesthetic_analysis(self, clip_blip_analysis: Dict) -> Dict[str, Any]:
        """Perform aesthetic analysis including proportional harmony, visual balance, style consistency, and contextual fit"""
        analysis = {
            "proportional_harmony": 0.0,
            "visual_balance": 0.0,
            "style_consistency": 0.0,
            "contextual_fit": 0.0,
            "issues": [],
            "recommendations": []
        }
        
        if "analysis" in clip_blip_analysis:
            insights = clip_blip_analysis["analysis"].get("combined_insights", {})
            
            # Proportional Harmony
            design_scores = insights.get("design_quality", {})
            if design_scores:
                analysis["proportional_harmony"] = sum(design_scores.values()) / len(design_scores) * 100
            
            # Visual Balance
            style_scores = insights.get("architectural_style", {})
            if style_scores:
                analysis["visual_balance"] = max(style_scores.values()) * 100
            
            # Style Consistency
            if style_scores:
                consistency_score = 1 - (max(style_scores.values()) - min(style_scores.values()))
                analysis["style_consistency"] = consistency_score * 100
            
            # Contextual Fit
            functional_scores = insights.get("functional_aspects", {})
            if functional_scores:
                analysis["contextual_fit"] = sum(functional_scores.values()) / len(functional_scores) * 100
        
        # Issues and recommendations
        if analysis["proportional_harmony"] < 60:
            analysis["issues"].append("Poor proportional harmony")
            analysis["recommendations"].append("Review design proportions and relationships")
        
        if analysis["style_consistency"] < 70:
            analysis["issues"].append("Inconsistent design style")
            analysis["recommendations"].append("Maintain consistent architectural style throughout")
        
        return analysis
    
    def _perform_accessibility_analysis(self, detections: List[Dict]) -> Dict[str, Any]:
        """Perform accessibility analysis for universal design"""
        analysis = {
            "wheelchair_accessibility": 0.0,
            "wayfinding": 0.0,
            "clearance_spaces": 0.0,
            "ramp_access": 0.0,
            "issues": [],
            "recommendations": []
        }
        
        element_types = [d["class_name"] for d in detections]
        
        # Wheelchair Accessibility
        accessibility_elements = ["door", "corridor", "circulation_node"]
        accessibility_count = sum(1 for elem in element_types if elem in accessibility_elements)
        analysis["wheelchair_accessibility"] = min(100, (accessibility_count / max(1, len(element_types))) * 150)
        
        # Wayfinding
        wayfinding_elements = ["text_label", "arrow", "elevation_marker", "north_arrow"]
        wayfinding_count = sum(1 for elem in element_types if elem in wayfinding_elements)
        analysis["wayfinding"] = min(100, (wayfinding_count / max(1, len(element_types))) * 200)
        
        # Clearance Spaces
        if "corridor" in element_types:
            analysis["clearance_spaces"] = 80  # Good clearance
        elif "door" in element_types:
            analysis["clearance_spaces"] = 60  # Moderate clearance
        else:
            analysis["clearance_spaces"] = 20  # Poor clearance
        
        # Ramp Access
        if "staircase" in element_types:
            analysis["ramp_access"] = 40  # Stairs present but no ramps
            analysis["issues"].append("Stairs present but no ramps detected")
            analysis["recommendations"].append("Consider adding ramps for accessibility")
        else:
            analysis["ramp_access"] = 80  # No stairs, potentially accessible
        
        # Overall issues
        if analysis["wheelchair_accessibility"] < 60:
            analysis["issues"].append("Poor wheelchair accessibility")
            analysis["recommendations"].append("Improve circulation and access for wheelchair users")
        
        return analysis
    
    def _perform_sustainability_analysis(self, detections: List[Dict], clip_blip_analysis: Dict) -> Dict[str, Any]:
        """Perform sustainability analysis including energy efficiency, materials, and site response"""
        analysis = {
            "energy_efficiency": 0.0,
            "sustainable_materials": 0.0,
            "site_response": 0.0,
            "passive_design": 0.0,
            "issues": [],
            "recommendations": []
        }
        
        element_types = [d["class_name"] for d in detections]
        
        # Energy Efficiency
        efficiency_elements = ["window", "shading_device", "sun_path"]
        efficiency_count = sum(1 for elem in element_types if elem in efficiency_elements)
        analysis["energy_efficiency"] = min(100, (efficiency_count / max(1, len(element_types))) * 200)
        
        # Sustainable Materials
        material_elements = ["material_texture", "facade"]
        material_count = sum(1 for elem in element_types if elem in material_elements)
        analysis["sustainable_materials"] = min(100, (material_count / max(1, len(element_types))) * 150)
        
        # Site Response
        site_elements = ["tree", "sun_path", "north_arrow"]
        site_count = sum(1 for elem in element_types if elem in site_elements)
        analysis["site_response"] = min(100, (site_count / max(1, len(element_types))) * 200)
        
        # Passive Design
        passive_elements = ["window", "shading_device", "sun_path", "tree"]
        passive_count = sum(1 for elem in element_types if elem in passive_elements)
        analysis["passive_design"] = min(100, (passive_count / max(1, len(element_types))) * 150)
        
        # Issues and recommendations
        if analysis["energy_efficiency"] < 40:
            analysis["issues"].append("Poor energy efficiency")
            analysis["recommendations"].append("Add energy-efficient features like shading devices")
        
        if analysis["passive_design"] < 50:
            analysis["issues"].append("Limited passive design features")
            analysis["recommendations"].append("Consider passive solar design strategies")
        
        return analysis
    
    def _perform_circulation_analysis(self, detections: List[Dict]) -> Dict[str, Any]:
        """Perform circulation analysis including movement patterns and flow"""
        analysis = {
            "circulation_efficiency": 0.0,
            "flow_patterns": {},
            "bottlenecks": [],
            "connectivity": 0.0,
            "issues": [],
            "recommendations": []
        }
        
        element_types = [d["class_name"] for d in detections]
        
        # Circulation Efficiency
        circulation_elements = ["door", "corridor", "circulation_node", "staircase"]
        circulation_count = sum(1 for elem in element_types if elem in circulation_elements)
        total_elements = len(element_types)
        
        if total_elements > 0:
            analysis["circulation_efficiency"] = min(100, (circulation_count / total_elements) * 200)
        
        # Flow Patterns
        analysis["flow_patterns"] = {
            "linear": "corridor" in element_types,
            "radial": "circulation_node" in element_types,
            "vertical": "staircase" in element_types,
            "horizontal": "door" in element_types
        }
        
        # Connectivity
        if "corridor" in element_types and "door" in element_types:
            analysis["connectivity"] = 80  # Good connectivity
        elif "door" in element_types:
            analysis["connectivity"] = 60  # Moderate connectivity
        else:
            analysis["connectivity"] = 20  # Poor connectivity
        
        # Issues and recommendations
        if analysis["circulation_efficiency"] < 60:
            analysis["issues"].append("Poor circulation efficiency")
            analysis["recommendations"].append("Improve circulation patterns and add more access points")
        
        if analysis["connectivity"] < 50:
            analysis["issues"].append("Poor space connectivity")
            analysis["recommendations"].append("Improve connections between spaces")
        
        return analysis
    
    def _perform_lighting_analysis(self, detections: List[Dict], clip_blip_analysis: Dict) -> Dict[str, Any]:
        """Perform lighting analysis including natural and artificial lighting"""
        analysis = {
            "natural_lighting": 0.0,
            "artificial_lighting": 0.0,
            "glare_control": 0.0,
            "light_distribution": 0.0,
            "issues": [],
            "recommendations": []
        }
        
        element_types = [d["class_name"] for d in detections]
        
        # Natural Lighting
        natural_elements = ["window", "sun_path"]
        natural_count = sum(1 for elem in element_types if elem in natural_elements)
        analysis["natural_lighting"] = min(100, (natural_count / max(1, len(element_types))) * 200)
        
        # Glare Control
        if "shading_device" in element_types:
            analysis["glare_control"] = 80  # Good glare control
        elif "window" in element_types:
            analysis["glare_control"] = 40  # Moderate glare control
        else:
            analysis["glare_control"] = 20  # Poor glare control
        
        # Light Distribution
        if "window" in element_types and "corridor" in element_types:
            analysis["light_distribution"] = 70  # Good distribution
        elif "window" in element_types:
            analysis["light_distribution"] = 50  # Moderate distribution
        else:
            analysis["light_distribution"] = 20  # Poor distribution
        
        # Issues and recommendations
        if analysis["natural_lighting"] < 40:
            analysis["issues"].append("Insufficient natural lighting")
            analysis["recommendations"].append("Add more windows for natural light")
        
        if analysis["glare_control"] < 50:
            analysis["issues"].append("Poor glare control")
            analysis["recommendations"].append("Consider adding shading devices")
        
        return analysis
    
    def _perform_acoustics_analysis(self, detections: List[Dict]) -> Dict[str, Any]:
        """Perform acoustics analysis including sound isolation and echo control"""
        analysis = {
            "sound_isolation": 0.0,
            "echo_control": 0.0,
            "acoustic_comfort": 0.0,
            "noise_control": 0.0,
            "issues": [],
            "recommendations": []
        }
        
        element_types = [d["class_name"] for d in detections]
        
        # Sound Isolation
        isolation_elements = ["wall", "door"]
        isolation_count = sum(1 for elem in element_types if elem in isolation_elements)
        analysis["sound_isolation"] = min(100, (isolation_count / max(1, len(element_types))) * 150)
        
        # Echo Control
        if "wall" in element_types and "corridor" in element_types:
            analysis["echo_control"] = 60  # Moderate echo control
        elif "wall" in element_types:
            analysis["echo_control"] = 40  # Basic echo control
        else:
            analysis["echo_control"] = 20  # Poor echo control
        
        # Acoustic Comfort
        analysis["acoustic_comfort"] = (analysis["sound_isolation"] + analysis["echo_control"]) / 2
        
        # Issues and recommendations
        if analysis["sound_isolation"] < 50:
            analysis["issues"].append("Poor sound isolation")
            analysis["recommendations"].append("Improve wall and door construction for better sound isolation")
        
        return analysis
    
    def _perform_thermal_analysis(self, detections: List[Dict], clip_blip_analysis: Dict) -> Dict[str, Any]:
        """Perform thermal analysis including thermal comfort and climate response"""
        analysis = {
            "thermal_comfort": 0.0,
            "insulation": 0.0,
            "thermal_bridges": 0.0,
            "climate_response": 0.0,
            "issues": [],
            "recommendations": []
        }
        
        element_types = [d["class_name"] for d in detections]
        
        # Thermal Comfort
        thermal_elements = ["window", "shading_device", "wall"]
        thermal_count = sum(1 for elem in element_types if elem in thermal_elements)
        analysis["thermal_comfort"] = min(100, (thermal_count / max(1, len(element_types))) * 150)
        
        # Insulation
        if "wall" in element_types:
            analysis["insulation"] = 60  # Basic insulation
        else:
            analysis["insulation"] = 20  # Poor insulation
        
        # Climate Response
        climate_elements = ["sun_path", "shading_device", "tree"]
        climate_count = sum(1 for elem in element_types if elem in climate_elements)
        analysis["climate_response"] = min(100, (climate_count / max(1, len(element_types))) * 200)
        
        # Issues and recommendations
        if analysis["thermal_comfort"] < 50:
            analysis["issues"].append("Poor thermal comfort")
            analysis["recommendations"].append("Improve thermal design and insulation")
        
        if analysis["climate_response"] < 40:
            analysis["issues"].append("Poor climate response")
            analysis["recommendations"].append("Consider climate-responsive design strategies")
        
        return analysis
    
    def _generate_overall_assessment(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate overall assessment from all analysis categories"""
        overall = {
            "total_score": 0.0,
            "risk_level": "low",
            "strengths": [],
            "weaknesses": [],
            "priority_areas": []
        }
        
        # Calculate total score from all categories
        scores = []
        for category, analysis in analysis_results.items():
            if category in ["overall_assessment", "critical_issues", "recommendations"]:
                continue
            
            if isinstance(analysis, dict) and "score" in analysis:
                scores.append(analysis["score"])
            elif isinstance(analysis, dict):
                # Extract scores from sub-categories
                for key, value in analysis.items():
                    if isinstance(value, (int, float)) and "score" in key.lower():
                        scores.append(value)
        
        if scores:
            overall["total_score"] = sum(scores) / len(scores)
        
        # Determine risk level
        if overall["total_score"] < 40:
            overall["risk_level"] = "critical"
        elif overall["total_score"] < 60:
            overall["risk_level"] = "high"
        elif overall["total_score"] < 80:
            overall["risk_level"] = "medium"
        else:
            overall["risk_level"] = "low"
        
        # Identify strengths and weaknesses
        for category, analysis in analysis_results.items():
            if category in ["overall_assessment", "critical_issues", "recommendations"]:
                continue
            
            if isinstance(analysis, dict):
                for key, value in analysis.items():
                    if isinstance(value, (int, float)) and "score" in key.lower():
                        if value >= 80:
                            overall["strengths"].append(f"{category.replace('_', ' ').title()}: {value:.1f}")
                        elif value <= 40:
                            overall["weaknesses"].append(f"{category.replace('_', ' ').title()}: {value:.1f}")
        
        return overall
    
    def _extract_critical_issues(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Extract critical issues from all analysis categories"""
        critical_issues = []
        
        for category, analysis in analysis_results.items():
            if category in ["overall_assessment", "critical_issues", "recommendations"]:
                continue
            
            if isinstance(analysis, dict) and "issues" in analysis:
                critical_issues.extend(analysis["issues"])
        
        return critical_issues[:10]  # Limit to top 10 issues
    
    def _extract_recommendations(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Extract recommendations from all analysis categories"""
        recommendations = []
        
        for category, analysis in analysis_results.items():
            if category in ["overall_assessment", "critical_issues", "recommendations"]:
                continue
            
            if isinstance(analysis, dict) and "recommendations" in analysis:
                recommendations.extend(analysis["recommendations"])
        
        return recommendations[:15]  # Limit to top 15 recommendations 