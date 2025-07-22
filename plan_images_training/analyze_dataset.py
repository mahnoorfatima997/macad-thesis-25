#!/usr/bin/env python3
"""
Analyze Architectural Training Dataset
Shows statistics and insights about your training data (plans + elevations)
"""

from pathlib import Path
import json

def analyze_dataset():
    """Analyze the training dataset"""
    print("📊 ARCHITECTURAL TRAINING DATASET ANALYSIS")
    print("=" * 50)
    
    # Load class definitions from our reference
    classes = {}
    with open("class_reference.md", 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines:
            if line.strip().startswith('**') and ':' in line:
                parts = line.strip().split('**')
                if len(parts) >= 3:
                    class_info = parts[1].split(':')
                    if len(class_info) == 2:
                        try:
                            class_id = int(class_info[0])
                            class_name = class_info[1].strip()
                            classes[class_id] = class_name
                        except ValueError:
                            continue
    
    # Count annotations per class
    class_counts = {i: 0 for i in range(103)}
    total_annotations = 0
    plan_stats = {}
    elevation_stats = {}
    
    # Analyze each annotation file
    labels_dir = Path("labels/train")
    
    for label_file in labels_dir.glob("*.txt"):
        file_name = label_file.stem
        annotations = []
        
        with open(label_file, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line:
                    try:
                        parts = line.split()
                        if len(parts) == 5:
                            class_id = int(parts[0])
                            x_center = float(parts[1])
                            y_center = float(parts[2])
                            width = float(parts[3])
                            height = float(parts[4])
                            
                            # Validate coordinates
                            if (0 <= x_center <= 1 and 0 <= y_center <= 1 and 
                                0 < width <= 1 and 0 < height <= 1):
                                
                                annotation = {
                                    'class_id': class_id,
                                    'class_name': classes.get(class_id, f'unknown_{class_id}'),
                                    'x_center': x_center,
                                    'y_center': y_center,
                                    'width': width,
                                    'height': height,
                                    'area': width * height
                                }
                                
                                annotations.append(annotation)
                                class_counts[class_id] += 1
                                total_annotations += 1
                            else:
                                print(f"⚠️ Invalid coordinates in {file_name}.txt line {line_num}: {line}")
                    
                    except (ValueError, IndexError) as e:
                        print(f"⚠️ Error parsing {file_name}.txt line {line_num}: {line} - {e}")
        
        # Categorize as plan or elevation
        if file_name.startswith('plan_'):
            plan_stats[file_name] = {
                'total_elements': len(annotations),
                'classes_present': list(set(ann['class_id'] for ann in annotations)),
                'class_names': list(set(ann['class_name'] for ann in annotations)),
                'annotations': annotations
            }
        elif file_name.startswith('elevation_'):
            elevation_stats[file_name] = {
                'total_elements': len(annotations),
                'classes_present': list(set(ann['class_id'] for ann in annotations)),
                'class_names': list(set(ann['class_name'] for ann in annotations)),
                'annotations': annotations
            }
    
    # Print analysis
    print(f"📁 Dataset Overview:")
    print(f"   Total images: {len(plan_stats) + len(elevation_stats)}")
    print(f"   Plans: {len(plan_stats)}")
    print(f"   Elevations: {len(elevation_stats)}")
    print(f"   Total annotations: {total_annotations}")
    
    if len(plan_stats) > 0:
        plan_annotations = sum(stats['total_elements'] for stats in plan_stats.values())
        print(f"   Average per plan: {plan_annotations / len(plan_stats):.1f}")
    
    if len(elevation_stats) > 0:
        elevation_annotations = sum(stats['total_elements'] for stats in elevation_stats.values())
        print(f"   Average per elevation: {elevation_annotations / len(elevation_stats):.1f}")
    
    print(f"\n🏗️ Class Distribution:")
    used_classes = [(class_id, count) for class_id, count in class_counts.items() if count > 0]
    used_classes.sort(key=lambda x: x[1], reverse=True)
    
    for class_id, count in used_classes:
        percentage = (count / total_annotations) * 100
        class_name = classes.get(class_id, f'unknown_{class_id}')
        print(f"   {class_id:2d}. {class_name:<20} : {count:2d} ({percentage:5.1f}%)")
    
    print(f"\n📋 Plan Details:")
    for plan_name, stats in plan_stats.items():
        print(f"   {plan_name}: {stats['total_elements']} elements")
        print(f"      Classes: {', '.join(stats['class_names'])}")
    
    print(f"\n🏢 Elevation Details:")
    for elevation_name, stats in elevation_stats.items():
        print(f"   {elevation_name}: {stats['total_elements']} elements")
        print(f"      Classes: {', '.join(stats['class_names'])}")
    
    # Check for potential issues
    print(f"\n🔍 Quality Check:")
    
    # Check for balanced classes
    if used_classes:
        min_count = min(count for _, count in used_classes)
        max_count = max(count for _, count in used_classes)
        
        if max_count > 0:
            balance_ratio = min_count / max_count
            if balance_ratio < 0.1:
                print(f"   ⚠️ Class imbalance detected (ratio: {balance_ratio:.2f})")
                print(f"      Consider adding more examples of underrepresented classes")
            else:
                print(f"   ✅ Good class balance (ratio: {balance_ratio:.2f})")
    
    # Check for missing important classes
    important_classes = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]  # Core architectural elements
    missing_important = [class_id for class_id in important_classes if class_counts[class_id] == 0]
    if missing_important:
        print(f"   ⚠️ Missing important classes: {[classes.get(cid, f'unknown_{cid}') for cid in missing_important]}")
    else:
        print(f"   ✅ All important classes represented")
    
    # Recommendations
    print(f"\n💡 Recommendations:")
    
    total_images = len(plan_stats) + len(elevation_stats)
    if total_images < 10:
        print(f"   📈 Add more images (aim for 10-20 minimum)")
    
    if total_annotations < 100:
        print(f"   📈 Add more annotations per image")
    
    if used_classes and min(count for _, count in used_classes) < 2:
        print(f"   📈 Add more examples of underrepresented classes")
    
    print(f"   🎯 Current dataset size is good for initial testing")
    print(f"   🚀 Ready to start training!")
    
    return {
        'total_images': total_images,
        'total_plans': len(plan_stats),
        'total_elevations': len(elevation_stats),
        'total_annotations': total_annotations,
        'class_counts': class_counts,
        'plan_stats': plan_stats,
        'elevation_stats': elevation_stats
    }

def save_analysis_report(analysis_data):
    """Save analysis report to JSON file"""
    report_path = Path("dataset_analysis.json")
    
    # Convert Path objects to strings for JSON serialization
    serializable_data = {
        'total_images': analysis_data['total_images'],
        'total_plans': analysis_data['total_plans'],
        'total_elevations': analysis_data['total_elevations'],
        'total_annotations': analysis_data['total_annotations'],
        'class_counts': analysis_data['class_counts'],
        'plan_stats': {},
        'elevation_stats': {}
    }
    
    for plan_name, stats in analysis_data['plan_stats'].items():
        serializable_data['plan_stats'][plan_name] = {
            'total_elements': stats['total_elements'],
            'classes_present': stats['classes_present'],
            'class_names': stats['class_names']
        }
    
    for elevation_name, stats in analysis_data['elevation_stats'].items():
        serializable_data['elevation_stats'][elevation_name] = {
            'total_elements': stats['total_elements'],
            'classes_present': stats['classes_present'],
            'class_names': stats['class_names']
        }
    
    with open(report_path, 'w') as f:
        json.dump(serializable_data, f, indent=2)
    
    print(f"\n📄 Analysis report saved to: {report_path}")

if __name__ == "__main__":
    analysis_data = analyze_dataset()
    save_analysis_report(analysis_data) 