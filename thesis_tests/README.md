# MEGA Architectural Mentor - Test Dashboard

## Overview

This test dashboard implements a comprehensive testing environment for evaluating three different approaches to architectural design assistance:

1. **MENTOR (Experimental)**: Multi-agent system with Socratic scaffolding
2. **Generic AI (Control)**: Direct AI assistance (ChatGPT-like)
3. **No AI (Baseline)**: Traditional approach without AI assistance

The system captures detailed interaction data and generates linkographies for cognitive analysis.

## Installation

```bash
# From the thesis_tests directory
pip install -r requirements_tests.txt

# Download spaCy language model (for move parsing)
python -m spacy download en_core_web_sm
```

## Running the Test Dashboard

```bash
# From the project root directory
streamlit run thesis_tests/test_dashboard.py
```

## Test Structure

### Pre-Test (10 minutes)
- Critical Thinking Assessment (Halpern CTDA)
- Architectural Knowledge Baseline
- Spatial Reasoning Test

### Main Test Phases (45 minutes total)
1. **Ideation Phase** (15 minutes)
   - Concept development
   - Program definition
   - Initial design thinking

2. **Visualization Phase** (20 minutes)
   - Spatial representation
   - Sketch development
   - Visual analysis

3. **Materialization Phase** (20 minutes)
   - Technical development
   - Material specifications
   - Construction planning

### Post-Test (10 minutes)
- Design process reflection
- Knowledge transfer task

## Data Collection

### Design Moves
Every interaction is parsed into discrete design moves for linkography:
- Move type (analysis, synthesis, evaluation, transformation, reflection)
- Design phase (ideation, visualization, materialization)
- Cognitive operation (proposal, clarification, assessment, support, reference)
- Design focus (function, form, structure, material, environment, culture)
- Move source (user_generated, ai_provided, ai_prompted, self_generated)

### Linkography Generation
Real-time linkographic analysis using:
- Semantic similarity (all-MiniLM-L6-v2 embeddings)
- Temporal relationships
- Fuzzy link strength (0.35 threshold)
- Pattern detection (chunks, webs, sawteeth)

### Cognitive Metrics
Six key metrics tracked throughout:
1. **Cognitive Offloading Prevention (COP)**: Resistance to seeking direct answers
2. **Deep Thinking Engagement (DTE)**: Reflective thinking and reasoning depth
3. **Scaffolding Effectiveness (SE)**: Appropriateness of guidance
4. **Knowledge Integration (KI)**: Concept connection and synthesis
5. **Learning Progression (LP)**: Skill development over time
6. **Metacognitive Awareness (MA)**: Self-reflection and strategy awareness

## Output Data

### Session Files
- `test_data/session_[id].json`: Complete session metadata
- `test_data/moves_[id].csv`: All design moves with linkography data
- `test_data/interactions_[id].csv`: User-system interactions
- `test_data/metrics_[id].csv`: Cognitive metrics over time

### Linkography Files
- `linkography_data/linkography_[id].json`: Complete linkograph with metrics
- `linkography_data/linkography_moves_[id].jsonl`: Move-by-move log

## Test Groups Comparison

### MENTOR Group
- Socratic questioning approach
- Never provides direct answers
- Guides through scaffolding
- Encourages deep thinking
- Expected: High COP, DTE, SE scores

### Generic AI Group
- Direct assistance approach
- Provides solutions and examples
- Answers questions directly
- Offers recommendations
- Expected: Low COP, moderate DTE, low SE scores

### Control Group
- No AI assistance
- Static resources only
- Self-directed work
- Natural progression
- Expected: Perfect COP, variable DTE, self-scaffolding

## Analysis Pipeline

After data collection:
```bash
# Run benchmarking analysis
python benchmarking/run_benchmarking.py

# Launch results dashboard
python benchmarking/launch_dashboard.py
```

## Integration with Existing Systems

The test dashboard integrates with:
- Multi-agent orchestration system (MENTOR group)
- OpenAI API (Generic AI group)
- Linkography engine (all groups)
- Cognitive benchmarking pipeline

## Ethical Considerations

- Informed consent required
- Data anonymization implemented
- Participant can withdraw at any time
- Session data can be deleted on request

## Research Applications

This testing framework enables:
- Comparative analysis of AI assistance approaches
- Linkographic pattern analysis across conditions
- Cognitive development tracking
- Educational effectiveness measurement
- Design process documentation

## Contact

For questions or issues, please contact the research team.