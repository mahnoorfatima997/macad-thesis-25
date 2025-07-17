# Enhanced Architectural Critique System v2.0.0

A comprehensive, multimodal AI-powered system for architectural design analysis and feedback. This enhanced version provides robust, definitive critique through advanced object detection, segmentation, and spatial analysis.

## 🏗️ Overview

The Enhanced Architectural Critique System represents a significant evolution from basic object detection to a comprehensive analysis platform that provides:

- **Advanced Object Detection & Segmentation**: YOLO + SAM integration for precise element identification
- **Spatial Relationship Analysis**: Understanding how architectural elements interact
- **Comprehensive Critique Framework**: Multi-category analysis with severity scoring
- **Visual Feedback System**: Interactive annotations and visual explanations
- **Compliance Checking**: Automatic verification against architectural standards
- **Cost Estimation**: Implementation cost and difficulty assessment

## 🚀 Key Features

### Technical Architecture
- **YOLO Detection**: YOLOv8/YOLOv9 for architectural element detection
- **SAM Segmentation**: Meta's Segment Anything Model for pixel-perfect masks
- **OpenCV Processing**: Advanced image preprocessing and annotation
- **Multi-modal Analysis**: Interior, exterior, site plans, floor plans, sections, elevations

### Analysis Capabilities
- **Functional Efficiency**: Circulation, accessibility, space utilization
- **Aesthetic Principles**: Proportion, balance, rhythm, hierarchy
- **Technical Compliance**: Building codes, structural logic, sustainability
- **User Experience**: Ergonomics, wayfinding, comfort
- **Spatial Relationships**: Object interactions, alignments, conflicts

### Visual Feedback
- **Interactive Annotations**: Clickable critique points with detailed explanations
- **Color-coded Categories**: Visual distinction between critique types
- **Before/After Comparison**: Side-by-side original and analyzed images
- **Metrics Dashboard**: Real-time design quality indicators
- **Compliance Summary**: Visual compliance status and issues

## 📁 Project Structure

```
enhanced-architectural-critique/
├── enhanced_architectural_critique.py    # Main analysis engine
├── enhanced_config_manager.py           # Configuration management
├── enhanced_web_interface.py            # Web interface
├── config_manager.py                    # Legacy config (for compatibility)
├── arch_critique_main.py               # Legacy main app (for compatibility)
├── web_interface.py                    # Legacy web interface (for compatibility)
├── uploads/                            # Uploaded images
├── outputs/                            # Analysis results
├── cache/                              # Model cache and temporary files
├── requirements.txt                    # Python dependencies
└── ENHANCED_README.md                  # This file
```

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- CUDA-compatible GPU (recommended)
- 8GB+ RAM
- 10GB+ free disk space

### Setup

1. **Clone and navigate to the project**:
   ```bash
   cd enhanced-architectural-critique
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Download required models**:
   ```bash
   # YOLO model (auto-downloaded on first use)
   # SAM model (download manually)
   wget https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth
   ```

4. **Set up environment variables** (optional):
   ```bash
   export CUDA_VISIBLE_DEVICES=0  # Use specific GPU
   export PYTHONPATH="${PYTHONPATH}:$(pwd)"
   ```

## 🎯 Usage

### Web Interface (Recommended)

1. **Start the web server**:
   ```bash
   python enhanced_web_interface.py
   ```

2. **Open your browser**:
   ```
   http://localhost:5000
   ```

3. **Upload and analyze**:
   - Drag and drop or select an architectural image
   - Choose analysis mode (interior, exterior, site plan, etc.)
   - Adjust confidence threshold and critique limits
   - Click "Analyze Design"

### Command Line Interface

```python
from enhanced_architectural_critique import EnhancedArchitecturalCritiqueApp
from enhanced_config_manager import AnalysisMode

# Initialize the app
app = EnhancedArchitecturalCritiqueApp()

# Load and analyze image
app.load_image("path/to/your/image.jpg")
objects = app.detect_objects(confidence_threshold=0.5)
app.segment_objects()
analysis = app.analyze_spatial_relationships()
critiques = app.generate_critique_points(analysis)

# Generate outputs
app.create_visual_feedback("annotated_output.jpg")
report = app.generate_report("analysis_report.json")

print(f"Overall Score: {report['overall_score']:.1f}/10")
```

### Configuration Management

```python
from enhanced_config_manager import EnhancedConfigManager, AnalysisMode

# Create config manager
config_manager = EnhancedConfigManager()

# Apply specific analysis mode
config_manager.apply_analysis_mode(AnalysisMode.INTERIOR)

# Customize settings
config_manager.update_model_config(
    confidence_threshold=0.4,
    device="cuda"
)

config_manager.update_critique_config(
    max_critique_points=15,
    enable_cost_estimation=True
)
```

## 📊 Analysis Modes

### 1. Interior Analysis
- **Focus**: Functional layout, furniture placement, circulation
- **Detections**: Doors, windows, furniture, fixtures
- **Metrics**: Circulation efficiency, lighting quality, accessibility
- **Best for**: Room layouts, interior design, furniture arrangements

### 2. Exterior Analysis
- **Focus**: Building form, facade design, site integration
- **Detections**: Building mass, windows, doors, landscaping
- **Metrics**: Aesthetic balance, sustainability, technical compliance
- **Best for**: Building exteriors, facade design, site planning

### 3. Site Plan Analysis
- **Focus**: Site organization, circulation, zoning compliance
- **Detections**: Buildings, roads, parking, landscaping
- **Metrics**: Site efficiency, circulation patterns, sustainability
- **Best for**: Master planning, site development, urban design

### 4. Floor Plan Analysis
- **Focus**: Spatial organization, room relationships, circulation
- **Detections**: Rooms, doors, windows, structural elements
- **Metrics**: Spatial hierarchy, functional optimization, accessibility
- **Best for**: Building design, space planning, renovation

### 5. Section Analysis
- **Focus**: Vertical relationships, structural systems, spatial quality
- **Detections**: Floors, walls, structural elements, openings
- **Metrics**: Spatial quality, structural logic, lighting distribution
- **Best for**: Building sections, structural analysis, spatial studies

### 6. Elevation Analysis
- **Focus**: Facade composition, material expression, proportions
- **Detections**: Windows, doors, materials, architectural elements
- **Metrics**: Aesthetic composition, material harmony, proportions
- **Best for**: Facade design, material studies, aesthetic analysis

## 🎨 Critique Categories

### Functional (Red)
- Circulation efficiency
- Space utilization
- Functional relationships
- Operational flow

### Aesthetic (Green)
- Visual balance
- Proportion and scale
- Material harmony
- Design coherence

### Technical (Blue)
- Structural logic
- Building systems
- Construction feasibility
- Performance standards

### Accessibility (Yellow)
- Universal design
- Mobility considerations
- Safety compliance
- Inclusive design

### Sustainability (Magenta)
- Energy efficiency
- Environmental impact
- Resource optimization
- Green building standards

### Circulation (Cyan)
- Movement patterns
- Wayfinding
- Access points
- Flow optimization

### Lighting (Orange)
- Natural lighting
- Artificial lighting
- Light distribution
- Visual comfort

### Acoustics (Purple)
- Sound control
- Acoustic comfort
- Noise management
- Acoustic design

### Thermal (Deep Pink)
- Thermal comfort
- Energy performance
- Climate response
- Environmental control

## 📈 Scoring System

### Overall Score (1-10)
- **9-10**: Excellent design with minor improvements possible
- **7-8**: Good design with some areas for enhancement
- **5-6**: Average design requiring significant improvements
- **3-4**: Poor design with major issues
- **1-2**: Critical design problems requiring immediate attention

### Severity Levels
- **Critical (4)**: Major issues affecting safety, compliance, or functionality
- **High (3)**: Significant issues impacting user experience or performance
- **Medium (2)**: Moderate issues affecting design quality
- **Low (1)**: Minor issues for aesthetic or optimization improvements

### Impact Scoring
- **0.0-0.3**: Minimal impact on overall design
- **0.4-0.6**: Moderate impact requiring attention
- **0.7-0.9**: High impact affecting key design aspects
- **1.0**: Critical impact requiring immediate resolution

## 🔧 Configuration

### Model Configuration
```json
{
  "models": {
    "yolo_model_path": "yolov8n.pt",
    "sam_checkpoint": "sam_vit_h_4b8939.pth",
    "confidence_threshold": 0.5,
    "device": "auto",
    "use_half_precision": true
  }
}
```

### Analysis Configuration
```json
{
  "analysis": {
    "analysis_mode": "interior",
    "min_object_distance": 50.0,
    "density_threshold": 0.4,
    "enable_compliance_checking": true
  }
}
```

### Critique Configuration
```json
{
  "critique": {
    "max_critique_points": 15,
    "severity_weights": {
      "accessibility": 1.5,
      "functional": 1.2,
      "technical": 1.0
    },
    "enable_cost_estimation": true
  }
}
```

## 📋 Output Formats

### JSON Report
```json
{
  "analysis_metadata": {
    "timestamp": "2024-01-15T10:30:00",
    "analysis_mode": "interior",
    "total_objects": 25,
    "total_critique_points": 8
  },
  "detected_objects": [...],
  "spatial_relationships": [...],
  "design_metrics": {
    "circulation_efficiency": 0.85,
    "lighting_quality": 0.72,
    "accessibility_compliance": 0.91
  },
  "critique_points": [...],
  "overall_score": 7.8,
  "compliance_summary": {...},
  "improvement_priorities": [...]
}
```

### Visual Outputs
- **Annotated Image**: Original image with analysis overlays
- **Metrics Dashboard**: Visual representation of design scores
- **Compliance Summary**: Visual compliance status
- **Interactive Elements**: Clickable critique points

## 🚀 Performance Optimization

### GPU Acceleration
```python
# Enable CUDA acceleration
config_manager.update_model_config(device="cuda")

# Use half precision for faster inference
config_manager.update_model_config(use_half_precision=True)
```

### Memory Optimization
```python
# Limit memory usage
config_manager.update_performance_config(max_memory_usage=4096)

# Enable memory optimization
config_manager.update_performance_config(enable_memory_optimization=True)
```

### Caching
```python
# Enable result caching
config_manager.update_performance_config(enable_result_caching=True)

# Set cache size
config_manager.update_performance_config(max_cache_size=512)
```

## 🔍 Troubleshooting

### Common Issues

1. **Model Loading Errors**
   ```bash
   # Check model paths
   ls -la yolov8n.pt
   ls -la sam_vit_h_4b8939.pth
   
   # Re-download models if needed
   wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt
   ```

2. **CUDA Memory Issues**
   ```python
   # Reduce batch size
   config_manager.update_model_config(batch_size=1)
   
   # Use CPU if GPU memory insufficient
   config_manager.update_model_config(device="cpu")
   ```

3. **Slow Performance**
   ```python
   # Enable optimizations
   config_manager.update_performance_config(enable_gpu_acceleration=True)
   config_manager.update_performance_config(enable_multi_threading=True)
   ```

### Performance Tips

- Use GPU acceleration when available
- Adjust confidence threshold based on needs
- Limit maximum critique points for faster analysis
- Use appropriate analysis mode for your image type
- Enable caching for repeated analyses

## 🤝 Contributing

### Development Setup
```bash
# Clone repository
git clone <repository-url>
cd enhanced-architectural-critique

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/
```

### Adding New Features
1. Create feature branch
2. Implement functionality
3. Add tests
4. Update documentation
5. Submit pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **YOLO**: Ultralytics for object detection
- **SAM**: Meta AI for segmentation
- **OpenCV**: Computer vision library
- **Flask**: Web framework
- **Architectural Standards**: Based on international building codes and best practices

## 📞 Support

For questions, issues, or contributions:
- Create an issue on GitHub
- Check the documentation
- Review troubleshooting section
- Contact the development team

---

**Enhanced Architectural Critique System v2.0.0** - Transforming architectural analysis through AI-powered multimodal feedback. 