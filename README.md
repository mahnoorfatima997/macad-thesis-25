# 🏗️ MEGA Architectural Mentor

A sophisticated AI-powered architectural tutoring system that combines multi-agent learning, computer vision, and cognitive benchmarking to provide personalized architectural guidance.

## 🎯 Overview

The MEGA Architectural Mentor is a comprehensive AI system designed to help architecture students and professionals develop their design thinking through:

- **Multi-Agent Tutoring**: Sophisticated Socratic questioning and domain expertise
- **Computer Vision Analysis**: GPT Vision + SAM segmentation for architectural drawings
- **Cognitive Benchmarking**: Graph ML-based assessment of learning effectiveness
- **Flexible Input Modes**: Text-only, image-only, or combined analysis
- **Real-time Learning Assessment**: Dynamic cognitive analysis and skill tracking

## 🚀 Key Features

### 🤖 Multi-Agent System
- **Socratic Tutor Agent**: Guides critical thinking through strategic questioning
- **Domain Expert Agent**: Provides architectural knowledge and technical guidance
- **Cognitive Enhancement Agent**: Challenges assumptions and promotes deeper thinking
- **Context Agent**: Analyzes student state and conversation progression
- **Analysis Agent**: Performs visual and textual analysis of projects

### 🖼️ Computer Vision Integration
- **GPT Vision Analysis**: Comprehensive architectural drawing interpretation
- **SAM2 Segmentation**: Precise spatial element detection and segmentation
- **Design Insights**: Automated identification of strengths, issues, and suggestions
- **Visual Feedback**: Interactive visualizations of analysis results

### 📊 Cognitive Benchmarking
- **Graph ML Analysis**: Advanced pattern recognition in learning interactions
- **Proficiency Classification**: ML-based skill level assessment (Beginner → Expert)
- **Effectiveness Metrics**: Comparison with traditional tutoring methods
- **Interactive Dashboard**: Comprehensive visualization of learning progress

### 🎛️ Flexible Input Modes
- **Text Only**: Project descriptions without images
- **Image + Text**: Combined visual and textual analysis
- **Image Only**: Pure visual analysis of architectural drawings
- **Template Prompts**: Quick-start templates for common project types

### 🔄 Real-time Learning Assessment
- **Dynamic Cognitive Analysis**: Real-time assessment based on latest interactions
- **Skill Level Tracking**: Continuous monitoring of learning progression
- **Response Type Analysis**: Understanding of educational strategies employed
- **Agent Effectiveness**: Tracking which agents are most helpful

## 🏗️ System Architecture

```
MEGA Architectural Mentor
├── 🎯 Main Application (mega_architectural_mentor.py)
├── 🤖 Multi-Agent System (thesis-agents/)
│   ├── Analysis Agent
│   ├── Socratic Tutor Agent
│   ├── Domain Expert Agent
│   ├── Cognitive Enhancement Agent
│   └── Context Agent
├── 🖼️ Computer Vision (vision/)
│   ├── GPT Vision Analysis
│   └── SAM2 Segmentation
├── 📊 Benchmarking System (benchmarking/)
│   ├── Graph ML Analysis
│   ├── Evaluation Metrics
│   ├── Visualization Tools
│   └── Interactive Dashboard
└── 📚 Knowledge Base (knowledge_base/)
    ├── Vector Database
    └── Document Storage
```

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- OpenAI API key
- CUDA-compatible GPU (optional, for SAM2)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd macad-thesis-25
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements_mega.txt
   ```

3. **Set up environment variables**
   ```bash
   # Create .env file
   echo "OPENAI_API_KEY=your_api_key_here" > .env
   ```

4. **Install SAM2 (optional)**
   ```bash
   # For SAM2 segmentation capabilities
   pip install segment-anything-2
   ```

## 🚀 Usage

### Starting the Application

```bash
streamlit run mega_architectural_mentor.py
```

The application will open at `http://localhost:8501`

### Basic Workflow

1. **Select Input Mode**
   - Choose between Text Only, Image + Text, or Image Only
   - Enable/disable SAM segmentation analysis

2. **Choose Mentor Type**
   - **Socratic Agent**: Multi-agent system with sophisticated questioning
   - **Raw GPT**: Direct GPT responses for comparison

3. **Select Template (Optional)**
   - Choose from pre-built project templates
   - Or write your own project description

4. **Set Skill Level**
   - Beginner, Intermediate, or Advanced
   - Helps tailor the mentoring approach

5. **Upload Content**
   - Upload architectural drawings (if using image modes)
   - Describe your project goals and constraints

6. **Start Analysis**
   - Click "Start Analysis" to begin the comprehensive evaluation
   - View results and begin interactive conversation

### Advanced Features

#### Template Design Prompts
- **🏢 Sustainable Office Building**: Complete brief for tech company office
- **🏫 Community Learning Center**: Comprehensive educational hub project

#### Benchmarking Dashboard
- Access via sidebar button
- View cognitive analysis results
- Track learning progression
- Compare with baseline methods

## 📊 Benchmarking System

### Running Cognitive Analysis

1. **Collect Data**: Use the main application normally
2. **Run Benchmarking**: Click "🔬 Run Benchmarking" in sidebar
3. **View Results**: Click "📈 View Dashboard" for interactive analysis

### Dashboard Features

- **Key Metrics Overview**: Total sessions, improvement rates
- **Proficiency Analysis**: Skill level distribution and characteristics
- **Cognitive Pattern Analysis**: Multi-dimensional assessment
- **Learning Progression**: Temporal analysis of improvement
- **Agent Effectiveness**: Coordination and response analysis

### Data Requirements

- **Basic Analysis**: 1+ sessions
- **Clustering & Benchmarks**: 3+ sessions recommended
- **Proficiency Classifier**: 5+ sessions required
- **Optimal Results**: 10+ sessions with varied interactions

## 🧠 Multi-Agent System Details

### Agent Roles

#### Analysis Agent
- **Purpose**: Initial project analysis and cognitive flag generation
- **Capabilities**: 
  - Building type detection
  - Cognitive gap identification
  - Visual analysis integration
  - Skill assessment

#### Socratic Tutor Agent
- **Purpose**: Guide critical thinking through strategic questioning
- **Capabilities**:
  - Student state analysis (confidence, understanding, engagement)
  - Conversation progression tracking
  - Adaptive response strategies
  - Clarifying, supportive, and challenging guidance

#### Domain Expert Agent
- **Purpose**: Provide architectural knowledge and technical guidance
- **Capabilities**:
  - Technical knowledge provision
  - Example generation
  - Best practices sharing
  - Contextual advice

#### Cognitive Enhancement Agent
- **Purpose**: Challenge assumptions and promote deeper thinking
- **Capabilities**:
  - Assumption identification
  - Alternative perspective generation
  - Critical thinking promotion
  - Creative problem-solving

#### Context Agent
- **Purpose**: Analyze conversation context and student state
- **Capabilities**:
  - Interaction type classification
  - Confidence level assessment
  - Engagement monitoring
  - Routing recommendations

## 🖼️ Computer Vision Features

### GPT Vision Analysis
- **Spatial Elements**: Detection of rooms, corridors, structural elements
- **Circulation Analysis**: Primary and secondary path identification
- **Design Insights**: Strengths, issues, and improvement suggestions
- **Contextual Understanding**: Integration with architectural principles

### SAM2 Segmentation
- **Precise Segmentation**: Pixel-perfect element separation
- **Spatial Relationships**: Understanding of element connections
- **Quantitative Analysis**: Area calculations and proportions
- **Visual Feedback**: Interactive segmentation overlays

## 📈 Learning Assessment

### Dynamic Cognitive Analysis
- **Real-time Updates**: Analysis based on latest interactions
- **Response Type Tracking**: Understanding of educational strategies
- **Learning Focus Identification**: Current educational priorities
- **Progress Monitoring**: Continuous skill development tracking

### Skill Assessment
- **Confidence Level**: Student self-assurance assessment
- **Understanding Level**: Comprehension depth evaluation
- **Engagement Level**: Participation and interest measurement
- **Agent Usage**: Tracking of most effective mentoring approaches

## 🔧 Configuration

### Environment Variables
```bash
OPENAI_API_KEY=your_openai_api_key
```

### Session State Management
The application uses Streamlit session state to maintain:
- User preferences and settings
- Conversation history
- Analysis results
- Learning progress

### Customization Options
- **CSS Styling**: Dark theme with custom styling
- **Agent Parameters**: Adjustable response characteristics
- **Benchmarking Settings**: Configurable analysis parameters
- **Visualization Options**: Customizable dashboard appearance

## 📁 Project Structure

```
macad-thesis-25/
├── mega_architectural_mentor.py    # Main application
├── requirements_mega.txt           # Dependencies
├── CLAUDE.md                       # Development documentation
├── thesis-agents/                  # Multi-agent system
│   ├── agents/                     # Individual agents
│   ├── orchestration/              # LangGraph orchestrator
│   ├── vision/                     # Computer vision components
│   └── data_collection/            # Interaction logging
├── benchmarking/                   # Cognitive analysis system
│   ├── benchmark_dashboard.py      # Interactive dashboard
│   ├── graph_ml_benchmarking.py    # Graph ML analysis
│   ├── evaluation_metrics.py       # Assessment metrics
│   └── results/                    # Analysis outputs
├── src/core/detection/             # SAM2 integration
├── segment-anything-2/             # SAM2 implementation
├── knowledge_base/                 # Document storage
├── thesis_data/                    # User interaction data
└── lib/                           # External libraries
```

## 🐛 Troubleshooting

### Common Issues

1. **SAM2 Import Error**
   ```bash
   pip install segment-anything-2
   ```

2. **OpenAI API Error**
   - Verify API key in environment variables
   - Check API quota and billing

3. **Memory Issues**
   - Reduce image resolution
   - Disable SAM analysis for large images

4. **Benchmarking Dashboard Not Loading**
   - Ensure sufficient interaction data (3+ sessions)
   - Check file permissions in benchmarking/results/

### Performance Optimization

- **GPU Acceleration**: Enable CUDA for SAM2 processing
- **Image Optimization**: Compress images before upload
- **Session Management**: Clear session state periodically
- **Memory Management**: Monitor RAM usage during analysis

## 🔮 Future Enhancements

### Planned Features
- **Multi-language Support**: International architectural terminology
- **Advanced Visualizations**: 3D model analysis and feedback
- **Collaborative Learning**: Multi-user session support
- **Mobile Interface**: Responsive design for mobile devices
- **API Integration**: RESTful API for external applications

### Research Directions
- **Advanced Graph ML**: Enhanced cognitive pattern recognition
- **Personalized Learning**: Adaptive curriculum generation
- **Cross-cultural Analysis**: Cultural context in architectural design
- **Sustainability Focus**: Environmental impact assessment

## 📚 Academic Context

This system is designed for architectural education research, specifically investigating:
- **Cognitive Development**: How AI tutoring affects design thinking
- **Multi-Agent Learning**: Effectiveness of specialized agent coordination
- **Computer Vision in Education**: Visual analysis for architectural feedback
- **Benchmarking Methodologies**: Scientific evaluation of AI tutoring systems

## 🤝 Contributing

### Development Guidelines
1. **Code Style**: Follow PEP 8 standards
2. **Documentation**: Update relevant documentation
3. **Testing**: Add tests for new features
4. **Benchmarking**: Ensure new features don't degrade performance

### Research Collaboration
- **Data Sharing**: Anonymized interaction data for research
- **Methodology**: Collaborative development of assessment metrics
- **Publications**: Joint research on AI in architectural education

## 📄 License

[Add your license information here]

## 🙏 Acknowledgments

- **OpenAI**: GPT-4o and Vision API
- **Meta AI**: Segment Anything Model 2
- **Streamlit**: Web application framework
- **LangGraph**: Multi-agent orchestration
- **Academic Community**: Research and feedback

---

**🏗️ MEGA Architectural Mentor** - Advancing architectural education through AI-powered cognitive development and multi-agent learning systems. 