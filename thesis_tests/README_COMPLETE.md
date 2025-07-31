# MEGA Cognitive Benchmarking Test System

## Research Overview

This system implements a comprehensive cognitive benchmarking study comparing three different approaches to architectural design education:

### Test Conditions

1. **MENTOR Group (Experimental)**
   - Multi-agent AI system with Socratic questioning
   - Prevents cognitive offloading through scaffolding
   - Builds critical thinking skills progressively
   - Uses 5 specialized agents working in concert

2. **Generic AI Group (Control 1)**
   - Direct AI assistance like ChatGPT
   - Provides immediate answers and solutions
   - May enable cognitive offloading
   - Uses OpenAI GPT-4 API

3. **Control Group (Baseline)**
   - Traditional approach without AI assistance
   - Natural design thinking patterns
   - Baseline for comparison

## Key Research Objectives

- **Prove that scaffolding (MENTOR) is superior to direct AI assistance** for cognitive development
- **Measure cognitive offloading patterns** across all three conditions
- **Track design thinking processes** using real-time linkography
- **Quantify learning progression** through standardized metrics

## Cognitive Metrics Tracked

- **COP**: Cognitive Offloading Prevention
- **DTE**: Deep Thinking Engagement  
- **SE**: Scaffolding Effectiveness
- **KI**: Knowledge Integration
- **LP**: Learning Progression
- **MA**: Metacognitive Awareness

## Installation

### Basic Requirements (for Generic AI and Control groups)
```bash
pip install -r thesis_tests/requirements_tests.txt
python -m spacy download en_core_web_sm
```

### Full Requirements (to enable MENTOR group)
```bash
# Install multi-agent dependencies
pip install langgraph langchain langchain-openai

# Verify installation
python test_system_status.py
```

### Configure OpenAI API (for Generic AI group)
Create a `.env` file in the root directory:
```
OPENAI_API_KEY=your-api-key-here
```

## Running the Tests

### Option 1: Full System (Recommended)
```bash
python launch_full_test.py
```
This launches the complete dashboard supporting all three test conditions.

### Option 2: Minimal System (if MENTOR unavailable)
```bash
python launch_minimal_test.py
```
This runs only Generic AI and Control groups.

## Test Protocol

### 1. Pre-Test Assessment (10 minutes)
- Critical Thinking Assessment (Halpern CTDA)
- Architectural Knowledge Baseline
- Spatial Reasoning Test

### 2. Design Task (55 minutes)
- **Ideation Phase** (15 minutes): Concept development
- **Visualization Phase** (20 minutes): Spatial representation
- **Materialization Phase** (20 minutes): Technical development

### 3. Post-Test Assessment (10 minutes)
- Design process reflection
- Knowledge transfer assessment

## Linkography Analysis

The system uses Gabriela Goldschmidt's Linkography methodology to:
- Track design moves in real-time
- Analyze cognitive patterns
- Measure thinking depth and complexity
- Compare patterns across test conditions

### Key Linkography Metrics
- **Link Density**: Connectivity between design moves
- **Critical Moves**: High-impact design decisions
- **Move Types**: Analysis, synthesis, evaluation, transformation, reflection
- **Phase Balance**: Distribution across design phases

## Data Output

All session data is automatically saved:
- `thesis_tests/test_data/` - Session logs and cognitive metrics
- `thesis_tests/linkography_data/` - Linkography analysis
- `thesis_tests/uploads/` - User sketches and documents

### Export Format
- JSON files with complete session data
- CSV files for statistical analysis
- Linkography visualizations (when available)

## Research Validation

This system enables rigorous comparison of:
- **Cognitive development trajectories** across conditions
- **Design quality outcomes** with different AI support
- **Learning effectiveness** of scaffolding vs direct assistance
- **Long-term skill retention** (in follow-up studies)

## Expected Outcomes

The research hypothesis predicts:
1. **MENTOR group** will show:
   - Higher COP scores (less cognitive offloading)
   - Better long-term learning outcomes
   - Deeper design thinking patterns
   
2. **Generic AI group** will show:
   - Lower COP scores (more offloading)
   - Faster task completion but shallower learning
   - Dependency on AI for solutions

3. **Control group** will show:
   - Natural baseline patterns
   - Autonomous thinking development
   - Variable outcomes based on individual ability

## Troubleshooting

### "MENTOR unavailable" error
Install multi-agent dependencies:
```bash
pip install langgraph langchain langchain-openai
```

### OpenAI API errors
Ensure your `.env` file contains a valid API key.

### Import errors
Run the complete installation:
```bash
pip install -r thesis_tests/requirements_tests.txt
python -m spacy download en_core_web_sm
```

## Ethics and Privacy

- All participant data is anonymized
- Sessions can be terminated at any time
- Data is used only for research purposes
- FERPA compliant data handling

## Contact

For questions about this research system, please contact the MaCAD thesis team.