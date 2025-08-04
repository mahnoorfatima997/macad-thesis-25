# Comprehensive Metrics Mapping Documentation

## Overview
This document provides a complete mapping of all metrics tracked in the MEGA Architectural Mentor thesis project, including their data sources, calculation methods, and integration with the benchmarking dashboard.

## Core Cognitive Metrics

### 1. Cognitive Offloading Prevention (COP)
- **Description**: Measures the system's ability to prevent users from delegating critical thinking to AI
- **Data Source**: `interactions_*.csv` - `prevents_cognitive_offloading` column
- **Range**: 0.0 - 1.0
- **Calculation**: Average of all interaction scores
- **Dashboard Location**: Key Metrics section, box plots, time series

### 2. Deep Thinking Engagement (DTE)
- **Description**: Tracks how well the system encourages analytical and critical thinking
- **Data Source**: `interactions_*.csv` - `encourages_deep_thinking` column
- **Range**: 0.0 - 1.0
- **Calculation**: Average of all interaction scores
- **Dashboard Location**: Key Metrics section, cognitive patterns

### 3. Scaffolding Effectiveness (SE)
- **Description**: Measures quality of educational support provided
- **Data Source**: `interactions_*.csv` - `provides_scaffolding` column
- **Range**: 0.0 - 1.0
- **Calculation**: Average of all interaction scores
- **Dashboard Location**: Learning progression charts

### 4. Knowledge Integration (KI)
- **Description**: Tracks integration of knowledge base content
- **Data Source**: `interactions_*.csv` - `knowledge_integrated` column
- **Range**: 0.0 - 1.0
- **Calculation**: Ratio of interactions with knowledge integration
- **Dashboard Location**: Agent effectiveness section

### 5. Learning Progression (LP)
- **Description**: Measures skill development over time
- **Data Source**: Calculated from interaction patterns and assessment scores
- **Range**: 0.0 - 1.0
- **Calculation**: Slope of performance metrics over session time
- **Dashboard Location**: Learning progression timeline

### 6. Multi-Agent Coordination (MA)
- **Description**: Effectiveness of multi-agent system coordination
- **Data Source**: `interactions_*.csv` - `multi_agent_coordination` column
- **Range**: 0.0 - 1.0
- **Calculation**: Average coordination score for MENTOR group
- **Dashboard Location**: Agent effectiveness radar chart

## Anthropomorphism Metrics (Enhanced)

### 7. Professional Boundary Index (PBI)
- **Description**: Measures maintenance of professional boundaries in conversations
- **Data Sources**: 
  - `topic_drift_*.csv` - topic classifications and drift scores
  - Fields: `topic_classification`, `conversation_drift_score`, `professional_boundary_maintained`
- **Components**:
  - Topic Classification: architectural/personal/mixed/neutral
  - Conversation Drift Score: 0.0 - 1.0 (higher = more drift)
  - Boundary Maintenance: Boolean (drift < 0.3)
- **Dashboard Location**: Anthropomorphism Analysis > Professional Boundaries tab

### 8. Bias Resistance Score (BRS)
- **Description**: Measures user's resistance to AI suggestions and bias
- **Data Sources**:
  - `suggestion_tracking_*.csv` - AI suggestion acceptance/rejection data
  - Fields: `accepted`, `rejection_reason`, `alternative_generated`, `time_to_decision`
- **Components**:
  - Suggestion Rejection Rate: % of AI suggestions rejected
  - Alternative Generation: Count of user-generated alternatives
  - Decision Time: Average time to accept/reject suggestions
- **Dashboard Location**: Anthropomorphism Analysis > Bias Resistance tab

### 9. Cognitive Autonomy Index (CAI)
- **Description**: Overall measure of independent thinking
- **Calculation**: Composite of:
  - Time allocation ratio (independent work / total work time)
  - Suggestion rejection rate
  - Alternative solutions generated
- **Range**: 0.0 - 1.0
- **Dashboard Location**: Anthropomorphism Analysis > Overview

### 10. Neural Engagement Score (NES)
- **Description**: Tracks cognitive load and engagement patterns
- **Data Sources**: 
  - Design move complexity scores
  - Interaction frequency patterns
  - Response time variations
- **Dashboard Location**: Anthropomorphism Analysis > Neural Engagement tab

### 11. Deep Thinking Index (DTI)
- **Description**: Measures depth of architectural thinking
- **Data Sources**:
  - Input length and complexity
  - Technical vocabulary usage
  - Conceptual connections in design moves
- **Dashboard Location**: Cognitive Patterns section

## Time-Based Metrics

### 12. Time Allocation Ratio
- **Description**: Ratio of independent work time to AI interaction time
- **Data Source**: `time_tracking_*.csv`
- **Fields**: `ai_interaction_time`, `independent_work_time`, `time_allocation_ratio`
- **Calculation**: independent_time / (ai_time + independent_time)
- **Dashboard Location**: Anthropomorphism Analysis > Time Allocation tab

### 13. Session Duration Metrics
- **Description**: Various time-based measurements
- **Components**:
  - Total session time
  - Average interaction duration
  - Time between interactions
  - Phase durations (ideation/visualization/materialization)
- **Dashboard Location**: Technical Details section

## Linkography Metrics

### 14. Link Density
- **Description**: Connectivity between design moves
- **Data Source**: `moves_*.csv` - semantic and temporal links
- **Calculation**: Total links / Total moves
- **Dashboard Location**: Linkography Analysis section

### 15. Critical Move Ratio
- **Description**: Proportion of highly connected design moves
- **Data Source**: Calculated from linkograph structure
- **Threshold**: Moves with 5+ links
- **Dashboard Location**: Linkography Analysis > Critical Moves

### 16. Design Phase Balance
- **Description**: Distribution of moves across design phases
- **Categories**: Ideation, Visualization, Materialization
- **Dashboard Location**: Linkography Analysis > Phase Distribution

## Proficiency Classification Metrics

### 17. User Proficiency Level
- **Description**: Classification into beginner/intermediate/advanced/expert
- **Data Sources**: Composite of all cognitive metrics
- **ML Model**: Random Forest Classifier
- **Features**: COP, DTE, SE, KI, LP, MA scores
- **Dashboard Location**: Proficiency Analysis section

### 18. Performance Consistency
- **Description**: Variance in performance metrics
- **Calculation**: Standard deviation of cognitive scores
- **Dashboard Location**: Proficiency Analysis > Consistency Chart

## Data File Structure

### Primary Data Files (Standard)
- `session_*.json` - Complete session metadata
- `interactions_*.csv` - All user-AI interactions with cognitive scores
- `moves_*.csv` - Design moves for linkography analysis
- `metrics_*.csv` - Periodic cognitive metric snapshots

### Enhanced Data Files (New)
- `suggestion_tracking_*.csv` - AI suggestion acceptance/rejection tracking
- `time_tracking_*.csv` - Time allocation between AI and independent work
- `topic_drift_*.csv` - Topic classification and conversation drift analysis

## Integration Points

### 1. Benchmarking Dashboard
- Loads all CSV files from `thesis_data/` directory
- Aggregates metrics across sessions
- Generates visualizations for each metric category
- Exports comprehensive reports

### 2. Test Dashboard
- Real-time metric calculation during sessions
- Automatic logging to all CSV files
- Enhanced tracking through `TestSessionLogger`

### 3. Data Validation
- `DataValidator` class ensures data authenticity
- Checks for mock data patterns
- Validates timing constraints
- Ensures data consistency

## Usage Guidelines

### For Researchers
1. All metrics are automatically logged during test sessions
2. Enhanced metrics require using the updated `logging_system.py`
3. Run benchmarking analysis with: `python benchmarking/run_benchmarking.py`
4. View results in dashboard: `streamlit run benchmarking/benchmark_dashboard.py`

### For Developers
1. Add new metrics to `TestSessionLogger` in `logging_system.py`
2. Create corresponding CSV headers in `_initialize_csv_files()`
3. Update dashboard to visualize new metrics
4. Document metric calculations in this file

## Validation Requirements
- Minimum 5 sessions for proficiency classification
- At least 10 interactions per session for reliable metrics
- Time tracking requires consistent session flow
- Topic classification needs meaningful user inputs

## Export Formats
- JSON: Complete session data with nested structures
- CSV: Tabular data for statistical analysis
- Aggregated reports: Summary statistics across sessions
- Visualization exports: PNG/HTML charts from dashboard