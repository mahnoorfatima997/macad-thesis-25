# Unified Architectural Dashboard

A comprehensive AI-powered architectural mentoring and research system that combines multi-agent cognitive enhancement with flexible input modes for thesis research and educational applications.

## 🌟 Key Features

### **Multi-Modal Input Support**
- **Text Only**: Describe your architectural project without images
- **Image + Text**: Upload architectural drawings and provide descriptions
- **Image Only**: Analyze architectural drawings using GPT Vision

### **Research-Focused Mentor Comparison**
- **Socratic Agent**: Multi-agent system with cognitive enhancement and guided questioning
- **Raw GPT**: Direct GPT responses for research comparison and baseline testing

### **Comprehensive Analysis Dashboard**
- **Cognitive Analysis**: Real-time assessment of learning journey and design phase
- **Learning Insights**: Identification of cognitive challenges and opportunities
- **Project Context**: Building type analysis, program requirements, and missing considerations
- **Smart Recommendations**: Phase-specific guidance and focus areas
- **Progress Visualization**: Phase completion tracking with meaningful status indicators

### **Advanced Research Metrics**
- **Scientific Data Collection**: Comprehensive interaction logging for thesis research
- **Cognitive Metrics**: COP (Cognitive Offloading Prevention), DTE (Deep Thinking Engagement), KI (Knowledge Integration) scores
- **Phase Progression**: Detailed tracking through ideation, visualization, and materialization phases
- **Enhanced Data Export**: Session data, scientific metrics, and research-ready CSV/JSON formats

### **Phase-Based Learning System**
- **Milestone Tracking**: Progress through specific architectural design milestones
- **Adaptive Questioning**: Socratic dialogue system that adapts to student progress
- **Learning Assessment**: Real-time evaluation of confidence, understanding, and engagement levels

## 🏗️ Architecture

### **Modular Structure**
```
dashboard/
├── __init__.py                 # Package initialization
├── README.md                   # This documentation
├── unified_dashboard.py        # Main dashboard class
├── config/
│   ├── __init__.py
│   └── settings.py            # Configuration settings and constants
├── core/
│   ├── __init__.py
│   └── session_manager.py     # Session state management
├── ui/
│   ├── __init__.py
│   ├── chat_components.py     # Chat interface components
│   ├── sidebar_components.py  # Sidebar functionality
│   ├── styles.py             # CSS styling
│   └── analysis_components.py # Analysis dashboard components
├── processors/
│   ├── __init__.py
│   ├── mode_processors.py     # Different AI mode processors
│   └── raw_gpt_processor.py   # Raw GPT comparison processor
└── analysis/
    ├── __init__.py
    └── phase_analyzer.py      # Phase progression analysis
```

### **Core Components**

#### **UnifiedArchitecturalDashboard**
Main orchestrator class that manages the entire dashboard experience:
- Handles input mode selection and validation
- Manages mentor type switching for research comparison
- Coordinates analysis pipeline and results display
- Integrates with thesis research data collection

#### **ModeProcessor**
Processes user input through different AI systems:
- **Socratic Agent Mode**: Full multi-agent system with cognitive enhancement
- **Raw GPT Mode**: Direct GPT responses for research comparison
- **Generic AI/Control Modes**: Additional testing modes for research

#### **Analysis Components**
Comprehensive analysis dashboard with:
- **Cognitive Analysis Dashboard**: Expandable section with learning journey insights
- **Metrics Summary**: 4-column layout showing phase, balance, progress, and project type
- **Phase Progress Visualization**: Detailed progress bars with milestone tracking

## 🚀 Getting Started

### **Prerequisites**
- Python 3.8+
- OpenAI API key
- Required dependencies (see `requirements_mega.txt`)

### **Installation**
```bash
# Install dependencies
pip install -r requirements_mega.txt

# Set API key
export OPENAI_API_KEY="your-api-key-here"

# Run the dashboard
python mentor_dashboard.py
```

### **Usage**

1. **Choose Input Mode**: Select Text Only, Image + Text, or Image Only
2. **Select Mentor Type**: Choose Socratic Agent or Raw GPT for comparison
3. **Configure Project**: Use templates or describe your architectural project
4. **Start Analysis**: Begin the AI-powered mentoring session
5. **Engage in Dialogue**: Ask questions and receive guided feedback
6. **Monitor Progress**: Track your learning journey through the analysis dashboard
7. **Export Data**: Download session data for research analysis

## 🧪 Research Features

### **Thesis Data Collection**
- Comprehensive interaction logging with scientific metrics
- Phase progression tracking for cognitive assessment
- Mentor type comparison data for research analysis
- Export capabilities for statistical analysis

### **Scientific Metrics**
- **Cognitive Offloading Prevention (COP)**: Measures system's ability to prevent cognitive offloading
- **Deep Thinking Engagement (DTE)**: Tracks engagement with complex thinking processes
- **Knowledge Integration (KI)**: Assesses integration of architectural knowledge
- **Phase Confidence Scores**: Measures student confidence in different design phases

### **Data Export Formats**
- **JSON**: Complete session data with metadata
- **CSV**: Interaction logs for statistical analysis
- **Research Metrics**: Scientific measurements for thesis research

## 🎯 Educational Applications

### **Architectural Design Education**
- **Phase-Based Learning**: Structured progression through design phases
- **Cognitive Enhancement**: Prevents cognitive offloading while providing appropriate scaffolding
- **Multi-Modal Support**: Accommodates different learning styles and project types

### **Research Applications**
- **Comparative Studies**: Socratic Agent vs Raw GPT effectiveness
- **Input Mode Analysis**: Text vs Image vs Combined input effectiveness
- **Cognitive Load Assessment**: Real-time monitoring of student cognitive state

## 🔧 Configuration

### **Settings (dashboard/config/settings.py)**
- **Input Modes**: Text Only, Image + Text, Image Only
- **Mentor Types**: Socratic Agent, Raw GPT
- **Template Prompts**: Pre-configured project templates
- **Skill Levels**: Beginner, Intermediate, Advanced

### **Session Management**
- **Automatic Session Tracking**: Timestamps, participant IDs, session duration
- **State Persistence**: Maintains conversation history and analysis results
- **Reset Functionality**: Clean session restart capabilities

## 📊 Analysis Dashboard

### **Cognitive Analysis Dashboard**
Comprehensive expandable section showing:
- **Current Design Phase**: Phase identification with confidence scores
- **Learning Insights**: Cognitive challenges and learning opportunities
- **Project Context**: Building type, requirements, and missing considerations
- **Smart Recommendations**: Phase-specific guidance and next focus areas
- **Progress Summary**: Overall phase progress with meaningful status descriptions

### **Metrics Summary**
4-column layout displaying:
- **Current Phase**: Active design phase with completion percentage
- **Learning Balance**: Ratio of challenges to opportunities
- **Phase Progress**: Milestone completion tracking
- **Project Type**: Building type with complexity indicators

### **Phase Progress Visualization**
Detailed progress section with:
- **Progress Bars**: Visual representation of phase completion
- **Milestone Tracking**: Specific architectural milestones achieved
- **Activity Guidance**: Key activities for current phase
- **Recommendations**: Phase-specific suggestions and next steps

## 🔬 Research Integration

### **Thesis Data Pipeline**
1. **Real-time Collection**: Interactions logged during sessions
2. **Scientific Processing**: Metrics calculated using established cognitive frameworks
3. **Export Pipeline**: Multiple formats for different analysis needs
4. **Longitudinal Tracking**: Session progression over time

### **Comparative Analysis Support**
- **A/B Testing**: Socratic Agent vs Raw GPT comparison
- **Input Mode Studies**: Effectiveness across different input modalities
- **Cognitive Load Analysis**: Real-time assessment of student cognitive state
- **Learning Progression**: Phase-based advancement tracking

## 🤝 Integration Points

### **External Systems**
- **thesis-agents/**: Multi-agent orchestration system
- **phase_progression_system.py**: Socratic dialogue and phase management

### **Data Collection**
- **InteractionLogger**: Comprehensive session logging
- **thesis_data/**: Research data export directory
- **benchmarking/**: Performance analysis integration (optional)

## 🛠️ Development

### **Adding New Features**
1. **UI Components**: Add to appropriate `ui/` module
2. **Processing Logic**: Extend `processors/` modules
3. **Analysis Features**: Enhance `analysis/` modules
4. **Configuration**: Update `config/settings.py`

### **Testing**
- **Unit Tests**: Component-level testing
- **Integration Tests**: Full pipeline testing
- **Research Validation**: Metric accuracy verification

## 📈 Performance

### **Optimization Features**
- **Cached Resources**: Heavy components cached for performance
- **Lazy Loading**: Components loaded on demand
- **Session Persistence**: Efficient state management
- **Streamlined UI**: Responsive design with minimal overhead

## 🔒 Privacy & Ethics

### **Data Handling**
- **Local Storage**: Session data stored locally by default
- **Anonymization**: Participant data can be anonymized
- **Export Control**: Users control data export and retention
- **Research Ethics**: Designed for ethical research practices

## 📚 Documentation

### **API Documentation**
- Component-level documentation in each module
- Type hints throughout codebase
- Comprehensive docstrings

### **Research Documentation**
- Metric calculation methodologies
- Phase progression frameworks
- Cognitive assessment criteria

---

## 🎓 Academic Context

This dashboard is designed specifically for architectural design education research, with a focus on:
- **Cognitive Enhancement**: Supporting student thinking without offloading cognitive load
- **Phase-Based Learning**: Structured progression through architectural design phases
- **Comparative Research**: Enabling rigorous comparison between different AI mentoring approaches
- **Multi-Modal Learning**: Supporting diverse learning styles and project presentation methods

The system generates research-quality data suitable for thesis analysis, educational assessment, and cognitive load studies in architectural design education. 