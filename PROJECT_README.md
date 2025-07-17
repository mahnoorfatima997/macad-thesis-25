# Architectural Analysis Systems

A comprehensive collection of AI-powered systems for architectural analysis, featuring both site plan analysis and enhanced architectural critique.

## 🏗️ Project Overview

This project provides two distinct architectural analysis systems:

1. **Site Plan Analysis System** - Original system for analyzing architectural site plans using YOLO + GPT-4 Vision
2. **Enhanced Architectural Critique System** - Advanced system for comprehensive architectural design analysis and feedback

## 📁 Project Structure

```
macad-thesis-25/
├── app.py                     # Main site plan analysis application
├── scripts/                   # Site plan analysis modules
│   ├── detect_yolo.py         # YOLO object detection
│   ├── gpt4_vision_analysis.py # GPT-4 Vision semantic analysis
│   ├── preprocess.py          # Image preprocessing
│   ├── shape_detection.py     # Shape detection utilities
│   └── generate_report.py     # Report generation
├── utils/                     # Utility functions
│   ├── file_utils.py          # File management utilities
│   ├── helpers.py             # General helper functions
│   └── e_drive_setup.py       # Environment setup
├── enhanced_architectural_critique/  # Enhanced critique system
│   ├── enhanced_architectural_critique.py
│   ├── enhanced_config_manager.py
│   ├── enhanced_web_interface.py
│   ├── requirements_enhanced.txt
│   └── README.md
├── shared/                    # Shared resources
│   ├── yolov8n.pt            # YOLO model
│   ├── uploads/              # Uploaded images
│   ├── outputs/              # Analysis results
│   ├── cache/                # Model cache
│   └── README.md
├── documentation/             # Documentation
│   ├── README.md             # Site plan system docs
│   ├── ENHANCED_README.md    # Enhanced system docs
│   ├── MIGRATION_GUIDE.md    # Migration guide
│   └── README.md
├── data/                      # Input data directory
├── output/                    # Output directory
├── models/                    # Model directory
├── requirements.txt           # Site plan system dependencies
└── PROJECT_README.md         # This file
```

## 🚀 Quick Start

### Site Plan Analysis System (Original)

```bash
# Install dependencies
pip install -r requirements.txt

# Set up OpenAI API key
cp env_example.txt .env
# Edit .env and add your OpenAI API key

# Run analysis
python app.py data/your_site_plan.jpg
```

### Enhanced Architectural Critique System

```bash
cd enhanced_architectural_critique
pip install -r requirements_enhanced.txt
# Download SAM model: wget https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth
python enhanced_web_interface.py
```

## 🎯 System Comparison

| Feature | Site Plan Analysis | Enhanced Critique |
|---------|-------------------|-------------------|
| **Purpose** | Site plan analysis | Architectural critique |
| **AI Models** | YOLO + GPT-4 Vision | YOLO + SAM |
| **Analysis Type** | Semantic + Object Detection | Spatial + Design Critique |
| **Output** | Site constraints, recommendations | Design metrics, critique points |
| **Use Case** | Master planning, site development | Building design, interior analysis |
| **API Required** | OpenAI GPT-4 Vision | None (local processing) |
| **Speed** | Fast (10-30s) | Comprehensive (30-90s) |

## 📚 Documentation

- **Site Plan System**: `documentation/README.md`
- **Enhanced System**: `documentation/ENHANCED_README.md`
- **Migration Guide**: `documentation/MIGRATION_GUIDE.md`

## 🔧 Requirements

### Site Plan Analysis System
- Python 3.8+
- OpenAI API key
- 2GB RAM
- Basic GPU (optional)

### Enhanced Architectural Critique System
- Python 3.8+
- 8GB+ RAM
- CUDA-compatible GPU (recommended)
- 10GB+ disk space

## 🎨 Features

### Site Plan Analysis System
- YOLO object detection for site elements
- GPT-4 Vision semantic analysis
- Spatial constraint identification
- Zoning compliance checking
- Design recommendations
- Comprehensive reporting

### Enhanced Architectural Critique System
- Advanced object detection with YOLO + SAM
- 9 critique categories
- 6 analysis modes (interior, exterior, etc.)
- Comprehensive spatial analysis
- Compliance checking
- Cost estimation
- Interactive visual feedback

## 📊 Output Examples

### Site Plan Analysis Output
```json
{
  "analysis_id": "analysis_20241201_143022",
  "object_detection": {
    "detections": [...],
    "summary": {
      "total_detections": 15,
      "detection_summary": {"building": 5, "road": 3, ...}
    }
  },
  "semantic_analysis": {
    "spatial_constraints": "...",
    "zoning_compliance": "...",
    "design_recommendations": "..."
  }
}
```

### Enhanced Critique Output
```json
{
  "overall_score": 7.5,
  "design_metrics": {
    "circulation_efficiency": 0.85,
    "lighting_quality": 0.72,
    "accessibility_compliance": 0.91
  },
  "critique_points": [
    {
      "category": "circulation",
      "severity": 3,
      "title": "Circulation Issues",
      "impact_score": 0.75,
      "estimated_cost": "Medium to High"
    }
  ]
}
```

## 🛠️ Development

### Site Plan Analysis
- **Main App**: `app.py`
- **Modules**: `scripts/` directory
- **Utilities**: `utils/` directory

### Enhanced Critique
- **Main App**: `enhanced_architectural_critique/`
- **Configuration**: Enhanced config management
- **Web Interface**: Modern Flask interface

## 📞 Support

- **Site Plan Issues**: Check `documentation/README.md`
- **Enhanced System Issues**: Check `documentation/ENHANCED_README.md`
- **Migration Questions**: Check `documentation/MIGRATION_GUIDE.md`

## 🎓 Academic Use

This project is part of a Master's thesis in Architecture. Please respect academic integrity and cite appropriately.

---

**Choose the system that best fits your analysis needs!** 