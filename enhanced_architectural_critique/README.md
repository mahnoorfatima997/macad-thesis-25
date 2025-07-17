# Enhanced Architectural Critique System

This directory contains the enhanced, comprehensive architectural critique system for building design analysis.

## 📁 Contents

- `enhanced_architectural_critique.py` - Main enhanced application with comprehensive analysis
- `enhanced_config_manager.py` - Advanced configuration management with validation
- `enhanced_web_interface.py` - Modern, interactive web interface
- `requirements_enhanced.txt` - Python dependencies for enhanced system

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements_enhanced.txt

# Download SAM model (required)
wget https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth

# Run enhanced web interface
python enhanced_web_interface.py

# Or use command line
python enhanced_architectural_critique.py
```

## 🎯 Use Cases

- Professional architectural analysis
- Building design critique and feedback
- Interior and exterior design evaluation
- Compliance checking against architectural standards
- Detailed spatial analysis needed
- Cost estimation and prioritization
- Multiple analysis modes required

## 📊 Features

- 9 critique categories (functional, aesthetic, technical, accessibility, etc.)
- 6 analysis modes (interior, exterior, site plan, floor plan, section, elevation)
- Comprehensive spatial analysis with relationships
- Compliance checking against architectural standards
- Cost estimation and implementation difficulty
- Advanced configuration management
- Interactive visual feedback with metrics dashboard
- Priority-based critique system

## 🔗 Related Files

- Models: `../shared/yolov8n.pt` and `sam_vit_h_4b8939.pth`
- Uploads: `../shared/uploads/`
- Outputs: `../shared/outputs/`
- Cache: `../shared/cache/`

## ⚠️ Requirements

- Python 3.8+
- CUDA-compatible GPU (recommended)
- 8GB+ RAM
- 10GB+ free disk space

## 🔄 Difference from Site Plan Analysis

This system is different from the main site plan analysis system:

| Aspect | Site Plan Analysis | Enhanced Critique |
|--------|-------------------|-------------------|
| **Purpose** | Site plan analysis | Building design critique |
| **AI Models** | YOLO + GPT-4 Vision | YOLO + SAM |
| **Analysis Type** | Semantic + Object Detection | Spatial + Design Critique |
| **Use Case** | Master planning, site development | Building design, interior analysis |

For detailed documentation, see `../documentation/ENHANCED_README.md` 