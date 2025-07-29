# Cognitive Benchmarking System with Linkography Integration

This benchmarking system implements the Graph ML-based cognitive assessment framework with integrated linkography analysis based on Gabriela Goldschmidt's methodology. It analyzes user interactions, generates cognitive benchmarks, visualizes design thinking patterns, and provides comprehensive evaluation of the multi-agent tutoring system's effectiveness.

## Overview

The benchmarking system consists of five main components:

1. **Graph ML Benchmarking** (`graph_ml_benchmarking.py`)
   - Converts interaction data into graph structures
   - Implements Graph Neural Networks (GNN) for pattern analysis
   - Generates cognitive benchmarks based on user proficiency clusters

2. **Evaluation Metrics** (`evaluation_metrics.py`)
   - Comprehensive cognitive development assessment
   - Comparison with baseline traditional tutoring methods
   - Educational effectiveness measurement

3. **Visualization Tools** (`visualization_tools.py`)
   - Interactive graph visualizations
   - Proficiency dashboards
   - Cognitive flow diagrams
   - Temporal analysis charts

4. **User Proficiency Classifier** (`user_proficiency_classifier.py`)
   - Machine learning-based proficiency classification
   - Feature extraction from interaction patterns
   - Personalized recommendations generation

5. **Linkography Analysis** (NEW)
   - **Types** (`linkography_types.py`): Data models for design moves and links
   - **Engine** (`linkography_engine.py`): Fuzzy linkography with semantic embeddings
   - **Analyzer** (`linkography_analyzer.py`): Session analysis and move extraction
   - **Visualization** (`linkography_visualization.py`): Interactive PyVis visualizations
   - **Cognitive Mapping** (`linkography_cognitive_mapping.py`): Maps patterns to metrics

## Installation

1. Ensure the main Mega Architectural Mentor environment is activated:
   ```bash
   # Windows
   mega_env\Scripts\activate
   
   # Linux/Mac
   source mega_env/bin/activate
   ```

2. Install additional benchmarking dependencies:
   ```bash
   pip install -r benchmarking/requirements_benchmarking.txt
   ```
   
   This includes linkography-specific packages:
   - `sentence-transformers`: For semantic embeddings (all-MiniLM-L6-v2)
   - `faiss-cpu`: For efficient similarity search
   - `pyvis`: For interactive linkograph visualization

## Usage

### Data Requirements

The benchmarking system has minimum data requirements for different features:

- **Basic Analysis**: 1+ sessions (limited functionality)
- **Clustering & Benchmarks**: 3+ sessions recommended
- **Proficiency Classifier**: 5+ sessions required
- **Optimal Results**: 10+ sessions with varied user interactions

### Generating Test Data

For testing or when you don't have enough real sessions yet:

```bash
python benchmarking/generate_test_data.py
```

This creates 5 synthetic sessions with varied skill levels and interaction patterns.

### Running the Complete Benchmarking Pipeline

The easiest way to run the full benchmarking analysis:

```bash
python benchmarking/run_benchmarking.py
```

This will:
- Load all interaction data from `./thesis_data/`
- Process data into interaction graphs
- Train the GNN model
- Generate cognitive benchmarks
- Evaluate all sessions
- Train the proficiency classifier (if 5+ sessions available)
- Generate comprehensive visualizations
- Create linkography analysis for each session
- Export a detailed report with linkography insights

### Command Line Options

```bash
python benchmarking/run_benchmarking.py [OPTIONS]

Options:
  --data-dir PATH           Directory containing interaction data (default: ./thesis_data)
  --output-dir PATH         Directory for output files (default: ./benchmarking/results)
  --no-classifier          Skip training the proficiency classifier
  --no-visualizations      Skip generating visualizations  
  --no-report             Skip generating the final report
```

### Using Individual Components

#### 1. Graph ML Analysis Only
```python
from benchmarking.graph_ml_benchmarking import CognitiveBenchmarkGenerator

generator = CognitiveBenchmarkGenerator()
graph = generator.process_session_data("./thesis_data/interactions_session1.csv")
```

#### 2. Evaluate Specific Session
```python
from benchmarking.evaluation_metrics import evaluate_session_data

report = evaluate_session_data("./thesis_data/interactions_session1.csv")
```

#### 3. Classify User Proficiency
```python
from benchmarking.user_proficiency_classifier import UserProficiencyClassifier
import pandas as pd

classifier = UserProficiencyClassifier()
classifier.load_model("./benchmarking/results/proficiency_classifier.pkl")

session_data = pd.read_csv("./thesis_data/interactions_session1.csv")
result = classifier.classify_user(session_data)
print(f"Proficiency: {result['proficiency_level']} ({result['confidence']:.0%} confidence)")
```

#### 4. Generate Linkography Analysis
```python
from benchmarking.linkography_analyzer import LinkographySessionAnalyzer
from benchmarking.linkography_visualization import LinkographVisualizer

# Analyze a session
analyzer = LinkographySessionAnalyzer()
linkograph_session = analyzer.analyze_session_file("./thesis_data/interactions_session1.csv")

# Create visualizations
visualizer = LinkographVisualizer()
visualizer.create_interactive_linkograph(linkograph_session)
visualizer.create_pattern_analysis(linkograph_session)
```

## Output Structure

After running the benchmarking pipeline, you'll find:

```
benchmarking/results/
├── benchmark_report.json          # Detailed benchmark profiles
├── comprehensive_benchmark_report.json  # Full analysis report
├── benchmark_summary.md          # Human-readable summary
├── gnn_model.pkl                # Trained Graph Neural Network
├── proficiency_classifier.pkl    # Trained proficiency classifier
├── evaluation_reports/          # Individual session evaluations
│   ├── session_xxx_evaluation.json
│   └── ...
├── visualizations/              # Generated visualizations
│   ├── proficiency_dashboard.html
│   ├── benchmark_comparison.html
│   ├── cognitive_flow.html
│   ├── interaction_graph_1.html
│   ├── cognitive_load_distribution.png
│   ├── learning_progression.png
│   ├── agent_usage_distribution.png
│   └── proficiency_clusters.png
└── linkography/                 # Linkography analysis results
    ├── session_linkographs/     # Individual session linkographs
    │   ├── session_xxx_linkograph.json
    │   └── session_xxx_linkograph.html
    ├── pattern_analysis/        # Cognitive pattern recognition
    │   ├── cognitive_overload_patterns.json
    │   ├── creative_breakthrough_patterns.json
    │   └── design_fixation_patterns.json
    └── interactive_graphs/      # PyVis interactive visualizations
        ├── combined_linkograph.html
        └── phase_transitions.html
```

## Key Metrics Evaluated

### Educational Effectiveness
- **Cognitive Offloading Prevention Rate**: How well the system prevents direct answer-seeking
- **Deep Thinking Engagement**: Frequency of responses that promote critical analysis
- **Scaffolding Effectiveness**: Quality of cognitive support provided
- **Knowledge Integration**: How well external knowledge is incorporated

### Learning Progression
- **Skill Level Changes**: Tracking beginner → intermediate → advanced progression
- **Confidence Development**: How user confidence evolves
- **Metacognitive Awareness**: Self-reflection and learning awareness

### System Performance
- **Agent Coordination**: How well multiple agents work together
- **Routing Appropriateness**: Accuracy of agent selection for different contexts
- **Response Coherence**: Quality of multi-agent responses

### Linkography Metrics
- **Link Density**: Ratio of actual links to possible links (indicates cognitive engagement)
- **Critical Moves**: Design moves with high fore-links (generative thinking)
- **Chunk Development**: Clusters of interconnected moves (focused exploration)
- **Phase Balance**: Distribution across ideation/visualization/materialization
- **Semantic Coherence**: Strength of conceptual connections between moves
- **Pattern Recognition**:
  - **Cognitive Overload**: Low link density + high move frequency
  - **Design Fixation**: Repetitive moves with low diversity
  - **Creative Breakthrough**: Sudden increase in link density + critical moves

## Interpreting Results

### Benchmark Profiles
The system generates benchmarks for each proficiency level (beginner, intermediate, advanced, expert) with:
- Target metric ranges
- Recommended teaching strategies
- Progression indicators

### Effectiveness Ratings
- **Highly Effective**: System exceeds benchmarks (>80% on key metrics)
- **Effective**: System meets core objectives (60-80%)
- **Moderately Effective**: Room for improvement (40-60%)
- **Needs Improvement**: Significant enhancements required (<40%)

### Improvement Over Baseline
The system compares performance against traditional tutoring methods. Positive percentages indicate improvement:
- **>50%**: Significant improvement
- **20-50%**: Moderate improvement
- **0-20%**: Slight improvement
- **<0%**: Performing below baseline

## Customization

### Adding New Metrics
To add custom evaluation metrics, extend the `CognitiveMetricsEvaluator` class:

```python
def _measure_custom_metric(self, data: pd.DataFrame) -> float:
    # Your metric calculation
    return metric_value
```

### Modifying Visualizations
The visualization style can be changed:

```python
visualizer = CognitiveBenchmarkVisualizer(style='presentation')  # or 'scientific'
```

### Adjusting GNN Architecture
Modify the GNN model in `graph_ml_benchmarking.py`:

```python
self.gnn_model = CognitiveGNN(
    input_dim=16,
    hidden_dim=128,  # Increase for more complex patterns
    output_dim=4,    # Number of proficiency levels
    num_heads=8      # GAT attention heads
)
```

## Troubleshooting

### No Data Found
Ensure you have run some tutoring sessions first. The system needs interaction data in `./thesis_data/interactions_*.csv` format.

**Solution**: 
1. Run the main app and have some conversations: `streamlit run mega_architectural_mentor.py`
2. Click "Export Session Data" in the sidebar after each session
3. Or generate test data: `python benchmarking/generate_test_data.py`

### Insufficient Data for Training
The proficiency classifier needs at least 5 sessions. The GNN model works best with 10+ sessions.

**Error**: `ValueError: max() iterable argument is empty`
- This occurs when trying to cluster with less than 3 sessions
- The system now handles this gracefully with rule-based assignment

### Session Data Not Saving
Make sure you:
1. Have interactions with the AI (not just uploading an image)
2. Click the "Export Session Data" button in the sidebar
3. Check that `./thesis_data/` directory exists and contains CSV files

### Memory Issues
For large datasets, you can process sessions in batches:

```python
# Process first 50 sessions only
session_files = session_files[:50]
```

### Visualization Errors
Ensure all dependencies are installed, especially:
```bash
pip install plotly kaleido torch torch-geometric
```

## Research Context

This benchmarking system implements the methodology described in the thesis documents:
- Uses Graph ML for post-study analysis
- Implements cognitive scaffolding metrics
- Prevents cognitive offloading through measurement
- Supports the three-phase design process (Ideation → Visualization → Materialization)
- Integrates Gabriela Goldschmidt's linkography for design process visualization

### Linkography-Cognitive Metric Mapping

The system maps linkography patterns to cognitive benchmarking metrics:

| Linkography Pattern | Cognitive Metric | Interpretation |
|-------------------|------------------|----------------|
| High link density | Deep Thinking Engagement (DTE) | Sustained cognitive effort |
| Critical moves with fore-links | Knowledge Integration (KI) | Synthesis and generation |
| Sparse linkographs | Cognitive Offloading Prevention (COP) | Potential overload or disengagement |
| Web structures | Scaffolding Effectiveness (SE) | Successful cognitive support |
| Phase transitions | Learning Progression (LP) | Design process advancement |
| Chunk patterns | Metacognitive Awareness (MA) | Focused exploration phases |

The benchmarks generated help validate the thesis hypothesis that multimodal AI can enhance rather than replace human spatial design capabilities through real-time process visualization and analysis.

## Citation

If using this benchmarking system in research, please reference the MaCAD Thesis:
```
Multimodal AI Systems for Professional Spatial Design Workflows
SEDA, BIEL, MAHNOOR - MaCAD Thesis 2025
Institute for Advanced Architecture of Catalonia
```