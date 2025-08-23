# MEGA Architectural Mentor - Thesis Explanatory Materials

## Overview
This directory contains comprehensive explanatory materials for understanding the MEGA Architectural Mentor thesis project. These materials explain the complex workflows, data pipelines, cognitive metrics, and analysis methodologies used in this advanced AI-powered educational system.

## Contents Organization

### 📚 Documentation Files

1. **[01_system_architecture.md](01_system_architecture.md)**
   - Complete system architecture overview
   - Component interaction flows
   - Multi-agent orchestration details
   - Knowledge base and RAG system
   - Suitable for: Technical and non-technical audiences

2. **[02_cognitive_metrics_explained.md](02_cognitive_metrics_explained.md)**
   - All 11 cognitive metrics definitions
   - Mathematical formulas and calculations
   - Scientific research foundations
   - Graph Neural Network analysis
   - Linkography methodology
   - Suitable for: Researchers and educators

3. **[03_data_flow_visualization.md](03_data_flow_visualization.md)**
   - Complete data pipeline documentation
   - File format specifications
   - Processing stages explained
   - Visualization types and purposes
   - Dashboard structure overview
   - Suitable for: Data scientists and developers

4. **[04_testing_framework_methodology.md](04_testing_framework_methodology.md)**
   - Three-group experimental design
   - Testing environment comparisons
   - Assessment tools and criteria
   - Statistical validation methods
   - Research methodology
   - Suitable for: Academics and practitioners

5. **[technical_details.html](technical_details.html)**
   - Interactive technical documentation
   - Metric calculation formulas
   - Research citations and references
   - Implementation details
   - Suitable for: Technical implementation teams

### 🎨 Visual Diagrams

All diagrams are available in both PNG (high-resolution) and SVG (scalable) formats in the `diagrams/` folder:

1. **System Architecture Diagram**
   - Shows all 6 system layers
   - Component interactions
   - Technology stack

2. **Data Flow Pipeline Diagram**
   - 6-stage processing pipeline
   - Data transformation steps
   - Quality gates and validation

3. **Cognitive Metrics Calculation Flow**
   - 11 metrics visualization
   - Calculation engines
   - Aggregation methods

4. **Benchmarking Process Flowchart**
   - 9-step benchmarking pipeline
   - Parallel processing paths
   - Output generation

5. **Agent Orchestration Diagram**
   - Multi-agent coordination
   - LangGraph workflow
   - State management

6. **Linkography Analysis Visualization**
   - Design move analysis
   - Pattern recognition
   - Critical move identification

7. **Comparative Analysis Framework**
   - 3-group comparison methodology
   - Statistical analysis pipeline
   - Outcome measures

8. **Dashboard Structure Overview**
   - 12 dashboard sections
   - User interaction flow
   - Export capabilities

### 🔧 Generation Scripts

- **[generate_all_diagrams.py](generate_all_diagrams.py)** - Master script to regenerate all diagrams
- Individual diagram generation scripts in `diagrams/` folder

## Quick Start Guide

### For General Audiences
Start with **01_system_architecture.md** for a high-level overview, then explore the visual diagrams to understand system components.

### For Educators
Focus on **02_cognitive_metrics_explained.md** to understand the educational theory and assessment methods.

### For Researchers
Review **04_testing_framework_methodology.md** for experimental design and **02_cognitive_metrics_explained.md** for scientific foundations.

### For Technical Teams
Study **03_data_flow_visualization.md** for implementation details and **technical_details.html** for formulas and calculations.

## Key Concepts Explained

### Cognitive Metrics
- **COP**: Cognitive Offloading Prevention - Prevents dependency on AI for answers
- **DTE**: Deep Thinking Engagement - Promotes analytical reasoning
- **SE**: Scaffolding Effectiveness - Adaptive learning support
- **KI**: Knowledge Integration - Multi-source synthesis
- **LP**: Learning Progression - Skill development tracking
- **MA**: Metacognitive Awareness - Self-reflection development

### System Components
- **Multi-Agent System**: 5 specialized agents (Socratic, Domain Expert, Cognitive Enhancement, Analysis, Context)
- **RAG System**: Knowledge retrieval from architectural documents
- **Linkography Engine**: Real-time design process analysis
- **Graph ML Pipeline**: Pattern recognition and clustering
- **Benchmarking Dashboard**: Comprehensive visualization and analysis

### Testing Groups
1. **MENTOR Group**: Uses full multi-agent system with Socratic questioning
2. **Generic AI Group**: Direct AI assistance (ChatGPT-like)
3. **Control Group**: No AI assistance, static resources only

## Color Palette

All visualizations use the official thesis color palette:
- Primary Dark: `#4f3a3e`
- Primary Purple: `#5c4f73`
- Primary Violet: `#784c80`
- Primary Rose: `#b87189`
- Neutral Warm: `#dcc188`
- Accent Coral: `#cd766d`

## Regenerating Materials

To regenerate all diagrams:
```bash
cd thesis_explanatory_materials
python generate_all_diagrams.py
```

## Additional Resources

- **Thesis Repository**: The main codebase at `macad-thesis-25/`
- **Benchmarking Results**: `benchmarking/results/` for generated reports
- **Test Data**: `thesis_data/` for interaction logs and metrics
- **Knowledge Base**: `knowledge_base/` for RAG documents

## Contact and Support

For questions about these materials or the thesis project, please refer to the main repository documentation or contact the thesis supervisor.

---

*Generated: January 2025*
*MEGA Architectural Mentor - Advancing AI-Powered Architectural Education*