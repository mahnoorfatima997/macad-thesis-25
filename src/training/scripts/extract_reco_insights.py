#!/usr/bin/env python3
"""
ReCo Dataset Insights Extractor
Extract insights and statistics from the ReCo architectural dataset
"""

import json
import os
from pathlib import Path
from collections import Counter, defaultdict
import matplotlib.pyplot as plt
import numpy as np

class ReCoInsightsExtractor:
    """Extract insights from ReCo dataset"""
    
    def __init__(self, reco_path: str = "data/datasets/ReCo_geojson.json"):
        self.reco_path = Path(reco_path)
        self.insights = {
            "total_features": 0,
            "room_types": Counter(),
            "geometry_types": Counter(),
            "property_keys": set(),
            "coordinate_ranges": {"x": [], "y": []},
            "feature_sizes": []
        }
    
    def extract_insights(self, max_features: int = 1000):
        """Extract insights from ReCo dataset"""
        print("🔍 EXTRACTING RECO DATASET INSIGHTS")
        print("=" * 50)
        
        if not self.reco_path.exists():
            print(f"❌ ReCo dataset not found at {self.reco_path}")
            return False
        
        print(f"📁 Dataset size: {self.reco_path.stat().st_size / (1024**3):.2f} GB")
        
        try:
            with open(self.reco_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            features = data.get('features', [])
            print(f"📖 Reading {len(features)} features for analysis...")
            
            # Analyze first max_features for performance
            sample_size = min(max_features, len(features))
            for feature in features[:sample_size]:
                self._analyze_feature(feature)
            
            print(f"✓ Analyzed {sample_size} features")
            return True
            
        except Exception as e:
            print(f"❌ Error reading ReCo dataset: {e}")
            return False
    
    def _analyze_feature(self, feature: dict):
        """Analyze a single feature"""
        self.insights["total_features"] += 1
        
        # Analyze geometry
        geometry = feature.get("geometry", {})
        geom_type = geometry.get("type", "unknown")
        self.insights["geometry_types"][geom_type] += 1
        
        # Analyze properties
        properties = feature.get("properties", {})
        for key in properties.keys():
            self.insights["property_keys"].add(key)
        
        # Analyze room type
        room_type = properties.get("room_type", "unknown")
        self.insights["room_types"][room_type] += 1
        
        # Analyze coordinates
        coordinates = geometry.get("coordinates", [])
        if coordinates and geom_type == "Polygon":
            polygon = coordinates[0]  # First ring
            if polygon:
                x_coords = [coord[0] for coord in polygon]
                y_coords = [coord[1] for coord in polygon]
                
                self.insights["coordinate_ranges"]["x"].extend(x_coords)
                self.insights["coordinate_ranges"]["y"].extend(y_coords)
                
                # Calculate feature size
                if len(x_coords) > 1 and len(y_coords) > 1:
                    width = max(x_coords) - min(x_coords)
                    height = max(y_coords) - min(y_coords)
                    area = width * height
                    self.insights["feature_sizes"].append(area)
    
    def print_insights(self):
        """Print extracted insights"""
        print(f"\n📊 RECO DATASET INSIGHTS")
        print("=" * 60)
        
        print(f"📈 Total features analyzed: {self.insights['total_features']}")
        
        print(f"\n🏗️ Geometry Types:")
        for geom_type, count in self.insights["geometry_types"].most_common():
            percentage = (count / self.insights["total_features"]) * 100
            print(f"   {geom_type}: {count} ({percentage:.1f}%)")
        
        print(f"\n🏠 Room Types (Top 20):")
        for room_type, count in self.insights["room_types"].most_common(20):
            percentage = (count / self.insights["total_features"]) * 100
            print(f"   {room_type}: {count} ({percentage:.1f}%)")
        
        print(f"\n🔑 Property Keys Found:")
        for key in sorted(self.insights["property_keys"]):
            print(f"   - {key}")
        
        if self.insights["coordinate_ranges"]["x"]:
            x_coords = self.insights["coordinate_ranges"]["x"]
            y_coords = self.insights["coordinate_ranges"]["y"]
            
            print(f"\n📐 Coordinate Ranges:")
            print(f"   X: {min(x_coords):.2f} to {max(x_coords):.2f}")
            print(f"   Y: {min(y_coords):.2f} to {max(y_coords):.2f}")
        
        if self.insights["feature_sizes"]:
            sizes = self.insights["feature_sizes"]
            print(f"\n📏 Feature Sizes:")
            print(f"   Min area: {min(sizes):.2f}")
            print(f"   Max area: {max(sizes):.2f}")
            print(f"   Average area: {np.mean(sizes):.2f}")
            print(f"   Median area: {np.median(sizes):.2f}")
    
    def create_visualization(self):
        """Create visualizations of the insights"""
        print(f"\n📊 CREATING VISUALIZATIONS")
        print("=" * 50)
        
        # Create output directory
        output_dir = Path("output/reco_insights")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Room types distribution
        if self.insights["room_types"]:
            plt.figure(figsize=(12, 8))
            
            # Top 15 room types
            top_rooms = dict(self.insights["room_types"].most_common(15))
            
            plt.subplot(2, 2, 1)
            plt.bar(range(len(top_rooms)), list(top_rooms.values()))
            plt.title("Top 15 Room Types")
            plt.xlabel("Room Type")
            plt.ylabel("Count")
            plt.xticks(range(len(top_rooms)), list(top_rooms.keys()), rotation=45, ha='right')
            
            # Geometry types
            plt.subplot(2, 2, 2)
            geom_types = list(self.insights["geometry_types"].keys())
            geom_counts = list(self.insights["geometry_types"].values())
            plt.pie(geom_counts, labels=geom_types, autopct='%1.1f%%')
            plt.title("Geometry Types Distribution")
            
            # Feature sizes histogram
            if self.insights["feature_sizes"]:
                plt.subplot(2, 2, 3)
                plt.hist(self.insights["feature_sizes"], bins=50, alpha=0.7)
                plt.title("Feature Size Distribution")
                plt.xlabel("Area")
                plt.ylabel("Frequency")
            
            # Coordinate scatter plot (sample)
            if self.insights["coordinate_ranges"]["x"]:
                plt.subplot(2, 2, 4)
                # Sample 1000 points for visualization
                sample_size = min(1000, len(self.insights["coordinate_ranges"]["x"]))
                indices = np.random.choice(len(self.insights["coordinate_ranges"]["x"]), sample_size, replace=False)
                x_sample = [self.insights["coordinate_ranges"]["x"][i] for i in indices]
                y_sample = [self.insights["coordinate_ranges"]["y"][i] for i in indices]
                plt.scatter(x_sample, y_sample, alpha=0.5, s=1)
                plt.title("Coordinate Distribution (Sample)")
                plt.xlabel("X Coordinate")
                plt.ylabel("Y Coordinate")
            
            plt.tight_layout()
            plt.savefig(output_dir / "reco_insights.png", dpi=300, bbox_inches='tight')
            print(f"✓ Visualization saved to: {output_dir / 'reco_insights.png'}")
    
    def generate_training_recommendations(self):
        """Generate recommendations for training"""
        print(f"\n💡 TRAINING RECOMMENDATIONS")
        print("=" * 50)
        
        recommendations = []
        
        # Analyze room type distribution
        total_rooms = sum(self.insights["room_types"].values())
        if total_rooms > 0:
            # Find underrepresented classes
            avg_count = total_rooms / len(self.insights["room_types"])
            underrepresented = []
            overrepresented = []
            
            for room_type, count in self.insights["room_types"].items():
                if count < avg_count * 0.5:
                    underrepresented.append(room_type)
                elif count > avg_count * 2:
                    overrepresented.append(room_type)
            
            if underrepresented:
                recommendations.append(f"⚠️ Underrepresented classes: {', '.join(underrepresented[:5])}")
            
            if overrepresented:
                recommendations.append(f"📈 Overrepresented classes: {', '.join(overrepresented[:5])}")
        
        # Geometry analysis
        if self.insights["geometry_types"]:
            polygon_count = self.insights["geometry_types"].get("Polygon", 0)
            if polygon_count > 0:
                recommendations.append(f"✅ {polygon_count} polygon features available for training")
        
        # Coordinate analysis
        if self.insights["coordinate_ranges"]["x"]:
            x_range = max(self.insights["coordinate_ranges"]["x"]) - min(self.insights["coordinate_ranges"]["x"])
            y_range = max(self.insights["coordinate_ranges"]["y"]) - min(self.insights["coordinate_ranges"]["y"])
            recommendations.append(f"📐 Coordinate ranges: X={x_range:.2f}, Y={y_range:.2f}")
        
        # Print recommendations
        for rec in recommendations:
            print(f"   {rec}")
        
        return recommendations

def main():
    """Main function"""
    extractor = ReCoInsightsExtractor()
    
    # Extract insights
    if extractor.extract_insights(max_features=5000):
        # Print insights
        extractor.print_insights()
        
        # Create visualizations
        extractor.create_visualization()
        
        # Generate recommendations
        extractor.generate_training_recommendations()

if __name__ == "__main__":
    main() 