# 🏗️ Unified Architectural Dashboard

## Overview

The Unified Architectural Dashboard is a comprehensive Streamlit application that combines multiple AI-powered architectural design tools into a single, integrated interface. It serves as a research platform for evaluating different approaches to architectural design assistance and cognitive enhancement.

## 🎯 Purpose

This dashboard is designed for:
- **Research**: Evaluating the effectiveness of different AI assistance modes
- **Testing**: Conducting controlled experiments with architectural design tasks
- **Analysis**: Comprehensive cognitive benchmarking and performance tracking
- **Education**: Providing scaffolded learning experiences for architectural design

## 🏗️ Architecture

### Core Components

The dashboard integrates three main systems:

1. **Multi-Agent Mentor System** (`mega_architectural_mentor.py`)
   - Socratic questioning approach
   - Cognitive enhancement agents
   - Domain-specific architectural guidance

2. **Test Environment** (`thesis_tests/`)
   - Controlled testing scenarios
   - Data collection and logging
   - Performance metrics tracking

3. **Benchmarking System** (`benchmarking/`)
   - Cognitive pattern analysis
   - Learning progression tracking
   - Comparative performance evaluation

### System Integration

```
┌─────────────────────────────────────────────────────────────┐
│                    Unified Dashboard                        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ Main Chat   │  │ Test        │  │ Benchmarking│        │
│  │ Interface   │  │ Dashboard   │  │ Dashboard   │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ Multi-Agent │  │ Test        │  │ Cognitive   │        │
│  │ Orchestrator│  │ Environments│  │ Analyzer    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ Data        │  │ Session     │  │ Export      │        │
│  │ Collection  │  │ Management  │  │ System      │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Features

### 1. Main Chat Interface

**Purpose**: Primary interaction hub for architectural design assistance

**Features**:
- **Three Testing Modes**:
  - **MENTOR**: Full multi-agent system with cognitive enhancement
  - **GENERIC_AI**: Basic AI responses for comparison
  - **CONTROL**: No AI assistance for baseline testing

- **Project Templates**:
  - Sustainable Office Building
  - Community Learning Center
  - Residential Complex
  - Cultural Center

- **Skill Level Adaptation**:
  - Beginner, Intermediate, Advanced
  - Tailored guidance based on expertise level

- **Real-time Analysis**:
  - Design phase progression tracking
  - Learning insights and challenges identification
  - Session metrics and performance indicators

### 2. Test Dashboard

**Purpose**: Controlled research environment for experimental testing

**Features**:
- **Pre-test Assessment** (Optional):
  - Critical Thinking Assessment
  - Architectural Knowledge Baseline
  - Spatial Reasoning Test
  - **Bypass Option**: Skip pre-test to go directly to main test

- **Design Phases**:
  - **Ideation** (15 minutes): Concept development and program definition
  - **Visualization** (20 minutes): Spatial diagrams and sketches
  - **Materialization** (20 minutes): Technical development and detailing

- **Post-test Assessment**:
  - Design Process Reflection
  - Knowledge Transfer Challenge

- **Session Management**:
  - Real-time metrics display
  - Data export capabilities
  - Session control (pause, reset, complete)

### 3. Benchmarking Dashboard

**Purpose**: Comprehensive cognitive analysis and performance evaluation

**Launch Options**:
- **Integrated**: Runs within the unified dashboard
- **Separate Process**: Opens in new browser tab

**Features**:
- **Key Metrics & Performance Indicators**
- **Proficiency Analysis & Classification**
- **Cognitive Pattern Recognition**
- **Learning Progression Tracking**
- **Agent Effectiveness Analysis**
- **Comparative Analysis**
- **Anthropomorphism Analysis**
- **Linkography Analysis**
- **Graph ML Visualizations**
- **Technical Details & Export Options**

### 4. Data Collection & Analysis

**Purpose**: Comprehensive logging and analysis of user interactions

**Features**:
- **Interaction Logging**: All user inputs and system responses
- **Cognitive Metrics**: Understanding, confidence, engagement levels
- **Phase Tracking**: Design thinking phase progression
- **Session Analytics**: Duration, interaction patterns, learning outcomes
- **Export Capabilities**: JSON, CSV, Excel formats

## 🛠️ Setup & Installation

### Prerequisites

1. **Python Environment**:
   ```bash
   python 3.8+
   ```

2. **Required Packages**:
   ```bash
   pip install streamlit pandas plotly numpy
   ```

3. **API Key**:
   - OpenAI API key required
   - Set as environment variable: `OPENAI_API_KEY`
   - Or configure in Streamlit secrets

### Installation Steps

1. **Clone Repository**:
   ```bash
   git clone <repository-url>
   cd macad-thesis-25
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set API Key**:
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

4. **Run Dashboard**:
   ```bash
   streamlit run unified_architectural_dashboard.py
   ```

## 📖 Usage Guide

### Getting Started

1. **Launch Dashboard**:
   - Run `streamlit run unified_architectural_dashboard.py`
   - Open browser to `http://localhost:8501`

2. **Configure Session**:
   - Check API key status in sidebar
   - Select testing mode (MENTOR/GENERIC_AI/CONTROL)
   - Choose project template or write custom description

3. **Start Analysis**:
   - Click "Start Analysis" to begin
   - System will analyze your project and provide initial insights

### Main Chat Interface

1. **Mode Selection**:
   - **MENTOR**: Full multi-agent assistance with cognitive enhancement
   - **GENERIC_AI**: Basic AI responses for comparison
   - **CONTROL**: Minimal assistance for baseline testing

2. **Project Setup**:
   - Select from predefined templates
   - Or write custom project description
   - Choose skill level for tailored guidance

3. **Interaction**:
   - Ask questions about your design
   - Request reviews or improvements
   - Explore precedents and technical requirements

4. **Progress Tracking**:
   - View current design phase
   - Monitor learning insights
   - Track session metrics

### Test Dashboard

1. **Session Setup**:
   - Enter participant ID
   - Select test group (MENTOR/GENERIC_AI/CONTROL)
   - Choose to skip pre-test if desired

2. **Test Flow**:
   - Complete pre-test assessment (if not skipped)
   - Work through design phases
   - Complete post-test assessment

3. **Data Collection**:
   - All interactions automatically logged
   - Real-time metrics displayed
   - Export session data when complete

### Benchmarking Dashboard

1. **Launch Options**:
   - **Integrated**: Runs within unified dashboard
   - **Separate Process**: Opens in new browser tab

2. **Analysis Features**:
   - View comprehensive cognitive metrics
   - Analyze learning progression
   - Compare performance across groups
   - Export detailed reports

## 🔧 Configuration

### Environment Variables

```bash
OPENAI_API_KEY=your-api-key-here
```

### Streamlit Configuration

The dashboard uses custom CSS for dark theme styling and responsive design.

### Session State Management

The dashboard maintains session state for:
- Chat messages and conversation history
- Analysis results and metrics
- Test session data
- User preferences and settings

## 📊 Data Structure

### Interaction Data Model

```python
InteractionData(
    id=str,                    # Unique interaction ID
    session_id=str,            # Session identifier
    timestamp=datetime,        # Interaction timestamp
    phase=TestPhase,           # Design phase
    interaction_type=str,      # Type of interaction
    user_input=str,           # User's input
    system_response=str,       # System's response
    response_time=float,       # Response time in seconds
    cognitive_metrics=dict,    # Cognitive assessment metrics
    metadata=dict             # Additional metadata
)
```

### Session Data Model

```python
TestSession(
    id=str,                    # Session ID
    participant_id=str,        # Participant identifier
    test_group=TestGroup,      # Test group assignment
    start_time=datetime,       # Session start time
    end_time=datetime,         # Session end time
    metrics=dict              # Session metrics
)
```

## 🔍 Research Capabilities

### Experimental Design

The dashboard supports three-group experimental design:

1. **MENTOR Group**: Full multi-agent system with cognitive enhancement
2. **GENERIC_AI Group**: Basic AI assistance for comparison
3. **CONTROL Group**: Minimal assistance for baseline measurement

### Data Collection

- **Quantitative Metrics**: Response times, interaction counts, cognitive scores
- **Qualitative Data**: User inputs, system responses, design decisions
- **Behavioral Patterns**: Phase progression, learning trajectories, engagement levels

### Analysis Tools

- **Cognitive Benchmarking**: Pattern recognition and analysis
- **Learning Progression**: Trajectory analysis and prediction
- **Comparative Analysis**: Cross-group performance evaluation
- **Linkography Analysis**: Design process visualization

## 🚨 Troubleshooting

### Common Issues

1. **API Key Error**:
   - Ensure `OPENAI_API_KEY` is set correctly
   - Check environment variable or Streamlit secrets

2. **Import Errors**:
   - Verify all dependencies are installed
   - Check Python path configuration

3. **Dashboard Not Loading**:
   - Ensure Streamlit is running on correct port
   - Check browser compatibility

4. **Test Dashboard Issues**:
   - Verify `thesis_tests` directory structure
   - Check data model imports

### Error Messages

- **"API Key Missing"**: Set `OPENAI_API_KEY` environment variable
- **"Module Not Found"**: Install missing dependencies
- **"Dashboard Launch Failed"**: Check file paths and permissions

## 📈 Performance Optimization

### Best Practices

1. **Session Management**:
   - Reset sessions regularly to prevent memory issues
   - Export data before clearing sessions

2. **Data Collection**:
   - Monitor session size for large datasets
   - Use export features for data backup

3. **System Resources**:
   - Close unused browser tabs
   - Monitor memory usage during long sessions

## 🔮 Future Enhancements

### Planned Features

1. **Advanced Analytics**:
   - Machine learning-based pattern recognition
   - Predictive modeling for learning outcomes

2. **Enhanced Visualization**:
   - 3D design process visualization
   - Real-time collaboration features

3. **Integration Capabilities**:
   - CAD software integration
   - External data source connections

4. **Mobile Support**:
   - Responsive design for mobile devices
   - Touch-optimized interface

## 📚 Documentation

### Additional Resources

- **API Documentation**: See individual component READMEs
- **Research Methodology**: Refer to thesis documentation
- **Data Analysis**: Check benchmarking folder for analysis tools

### Support

For technical support or research questions:
- Check troubleshooting section
- Review component-specific documentation
- Contact development team

## 📄 License

This project is part of academic research. Please refer to the main repository for licensing information.

---

**Version**: 1.0  
**Last Updated**: December 2024  
**Maintainer**: Research Team 