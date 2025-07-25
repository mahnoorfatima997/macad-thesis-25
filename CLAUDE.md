# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the **Mega Architectural Mentor** - a MaCAD thesis project combining computer vision (GPT-4 Vision + SAM) with a multi-agent AI system for architectural education. It prevents cognitive offloading by enhancing critical thinking through Socratic questioning and cognitive scaffolding.

## Common Development Commands

```bash
# Setup (Windows)
python setup_mega.py               # Automated setup script
mega_env\Scripts\activate          # Activate virtual environment

# Setup (Linux/Mac)
python setup_mega.py
source mega_env/bin/activate

# Install dependencies
pip install -r requirements_mega.txt    # Full dependencies with SAM
pip install -r requirements.txt         # Core dependencies only
pip install -r benchmarking/requirements_benchmarking.txt  # Benchmarking dependencies

# Run applications
streamlit run mega_architectural_mentor.py    # Main unified app (GPT+SAM+Agents)
streamlit run thesis-agents/app.py            # Multi-agent system only
python main.py                                 # Simple unified engine

# Run cognitive benchmarking
python benchmarking/run_benchmarking.py       # Full benchmarking pipeline
python benchmarking/run_benchmarking.py --no-visualizations  # Skip visualizations
python benchmarking/run_benchmarking.py --data-dir ./custom_data  # Custom data directory

# Development tools
black .                    # Code formatting
flake8 .                  # Linting
pytest                    # Run tests (no test files currently exist)
```

## High-Level Architecture

The system consists of four major components working together:

### 1. Computer Vision Pipeline (`src/core/detection/`)
- **GPT-4 Vision**: Analyzes architectural drawings for elements, composition, and design principles
- **SAM (Segment Anything Model)**: Provides precise segmentation of identified elements
- **Integration**: `vision/gpt_sam_analyzer.py` combines both for comprehensive visual analysis

### 2. Multi-Agent System (`thesis-agents/`)
- **Orchestration**: LangGraph-based orchestrator manages agent interactions
- **Agents**:
  - `AnalysisAgent`: Processes visual artifacts and generates architectural insights
  - `SocraticTutorAgent`: Guides learning through questions, never providing direct answers
  - `DomainExpertAgent`: Provides specialized architectural knowledge
  - `CognitiveEnhancementAgent`: Monitors and prevents cognitive offloading
  - `ContextAgent`: Maintains conversation continuity and learning context
- **State Management**: Uses `ArchMentorState` to track conversation, visual artifacts, and student progress

### 3. Knowledge Base System
- **Vector Store**: ChromaDB for semantic search of architectural references
- **Documents**: 40+ architecture PDFs in `knowledge_base/downloaded_pdfs/`
- **Manager**: `knowledge_base/knowledge_manager.py` handles indexing and retrieval

### 4. Cognitive Benchmarking System (`benchmarking/`)
- **Graph ML Analysis**: `graph_ml_benchmarking.py` - Converts interactions to graphs and applies GNNs
- **Evaluation Metrics**: `evaluation_metrics.py` - Measures cognitive development and educational effectiveness
- **Visualization Tools**: `visualization_tools.py` - Creates interactive dashboards and analysis charts
- **Proficiency Classifier**: `user_proficiency_classifier.py` - ML-based user proficiency assessment
- **Pipeline Runner**: `run_benchmarking.py` - Orchestrates the complete benchmarking analysis

## Key Integration Points

### Unified Application Flow (`mega_architectural_mentor.py`):
1. User uploads architectural image
2. GPT-4 Vision + SAM analyze the image
3. Analysis results feed into multi-agent system
4. Agents engage in Socratic dialogue based on visual analysis
5. Knowledge base provides contextual references
6. Interactions logged for thesis research

### Critical Implementation Details:
- **State Persistence**: Uses Streamlit session state to maintain conversation context
- **Agent Communication**: All agents share `ArchMentorState` for coherent responses
- **Visual Context**: `VisualArtifact` class carries image analysis throughout conversation
- **Learning Tracking**: `StudentProfile` adapts agent responses to skill level

## Configuration

- **Main Config**: `config.json` - Model paths and feature flags
- **Environment**: `.env` file required with `OPENAI_API_KEY`
- **Model Downloads**: SAM models must be downloaded separately (see `install_grounded_sam.py`)

## Data Flow for Development

When modifying the system:
1. **Visual Analysis Changes**: Start with `src/core/detection/sam2_module_fixed.py` or `vision/gpt_sam_analyzer.py`
2. **Agent Behavior**: Modify individual agents in `thesis-agents/agents/`
3. **Orchestration Logic**: Update `orchestration/langgraph_orchestrator.py`
4. **UI/UX**: Changes in `mega_architectural_mentor.py` or `thesis-agents/app.py`
5. **Benchmarking Analysis**: Modify components in `benchmarking/` for evaluation changes

## Research Components

The system includes comprehensive thesis-specific data collection and analysis:

### Data Collection
- **Interaction Logger**: `data_collection/interaction_logger.py` tracks all user interactions
- **Metrics**: Response times, question types, cognitive load indicators
- **Export**: Use `export_thesis_ready_data()` for research analysis

### Cognitive Benchmarking
- **Graph ML Pipeline**: Analyzes interaction patterns using Graph Neural Networks
- **Proficiency Classification**: Categorizes users into beginner/intermediate/advanced/expert
- **Evaluation Metrics**: Measures cognitive offloading prevention, deep thinking engagement, scaffolding effectiveness
- **Visualization Suite**: Interactive dashboards, cognitive flow diagrams, temporal analysis
- **Benchmark Generation**: Creates proficiency-based benchmarks with progression indicators

### Running Benchmarking Analysis
```bash
# Full analysis pipeline
python benchmarking/run_benchmarking.py

# Output structure:
benchmarking/results/
├── benchmark_report.json              # Detailed benchmarks
├── comprehensive_benchmark_report.json # Full analysis
├── benchmark_summary.md              # Human-readable summary
├── gnn_model.pkl                    # Trained GNN model
├── proficiency_classifier.pkl       # Trained classifier
├── evaluation_reports/              # Per-session evaluations
└── visualizations/                  # Generated charts and graphs
```

### Key Thesis Metrics
- **Cognitive Offloading Prevention Rate**: Target >70%
- **Deep Thinking Engagement**: Target >60%
- **Improvement over Baseline**: Comparing to traditional tutoring methods
- **Learning Progression**: Tracking skill development across sessions