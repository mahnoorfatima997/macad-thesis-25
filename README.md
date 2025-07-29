# 🏗️ MEGA Architectural Mentor

## AI-Powered Architectural Education with Cognitive Enhancement

A comprehensive thesis project for MaCAD that combines cutting-edge computer vision (GPT-4 Vision + SAM), multi-agent AI systems, and cognitive benchmarking with linkography integration to revolutionize architectural education through preventing cognitive offloading and enhancing critical thinking.

---

## 🌟 Key Features

### 1. **Computer Vision Analysis**
- **GPT-4 Vision**: Analyzes architectural drawings for design elements, composition, and principles
- **SAM Integration**: Precise segmentation of architectural elements
- **Real-time Feedback**: Instant visual analysis of uploaded sketches and drawings

### 2. **Multi-Agent AI System**
- **Socratic Tutor**: Guides learning through questions, never providing direct answers
- **Domain Expert**: Offers specialized architectural knowledge when needed
- **Cognitive Enhancement Agent**: Monitors and prevents cognitive offloading
- **Context Agent**: Maintains conversation continuity and learning progression
- **Analysis Agent**: Processes visual artifacts and generates architectural insights

### 3. **Cognitive Benchmarking**
- **Six Core Metrics**: COP, DTE, SE, KI, LP, MA for comprehensive assessment
- **Graph ML Analysis**: Uses Graph Neural Networks for pattern recognition
- **Proficiency Classification**: Categorizes users from beginner to expert
- **Interactive Dashboards**: Real-time visualization of learning progress

### 4. **Linkography Integration** 🆕
- **Design Process Analysis**: Implements Gabriela Goldschmidt's linkography methodology
- **Real-time Linkograph Generation**: Visualizes design thinking patterns as they emerge
- **Fuzzy Linkography**: Uses semantic embeddings (all-MiniLM-L6-v2) for intelligent link detection
- **Pattern Recognition**: Identifies cognitive overload, design fixation, and creative breakthroughs
- **Interactive Visualizations**: PyVis-powered interactive linkographs in the dashboard

---

## 🚀 Quick Start

### Basic Setup (Without SAM)

```bash
# 1. Create virtual environment
python -m venv mega_env
mega_env\Scripts\activate  # Windows
source mega_env/bin/activate  # Mac/Linux

# 2. Install core dependencies
pip install -r requirements.txt

# 3. Set OpenAI API key
echo "OPENAI_API_KEY=your_key_here" > .env

# 4. Run the application
streamlit run mega_architectural_mentor.py
```

### Full Setup (With SAM + All Features)

```bash
# 1. Create virtual environment
python -m venv mega_env
mega_env\Scripts\activate  # Windows

# 2. Install all dependencies
pip install -r requirements_mega.txt

# 3. Install benchmarking dependencies (includes linkography)
pip install -r benchmarking/requirements_benchmarking.txt

# 4. Set OpenAI API key
echo "OPENAI_API_KEY=your_key_here" > .env

# 5. Run the application
streamlit run mega_architectural_mentor.py
```

---

## 📊 Cognitive Benchmarking & Linkography

### Running Analysis

```bash
# Full benchmarking pipeline
python benchmarking/run_benchmarking.py

# Generate test data (if needed)
python benchmarking/generate_test_data.py

# Launch interactive dashboard
python benchmarking/launch_dashboard.py

# Linkography-specific analysis
python benchmarking/linkography_analyzer.py
```

### Key Metrics

- **Cognitive Offloading Prevention (COP)**: >70% target
- **Deep Thinking Engagement (DTE)**: >60% target
- **Scaffolding Effectiveness (SE)**: Adaptive learning support
- **Knowledge Integration (KI)**: Cross-domain synthesis
- **Learning Progression (LP)**: Skill development tracking
- **Metacognitive Awareness (MA)**: Self-reflection capabilities

### Linkography Metrics

- **Link Density**: Measure of cognitive engagement intensity
- **Critical Moves**: Identification of key design decisions
- **Phase Balance**: Distribution across ideation/visualization/materialization
- **Pattern Detection**: Automated recognition of cognitive states

---

## 🏛️ Architecture

```
mega-architectural-mentor/
├── mega_architectural_mentor.py    # Main unified application
├── thesis-agents/                  # Multi-agent system
│   ├── agents/                     # Individual AI agents
│   ├── orchestration/              # LangGraph orchestrator
│   └── data_collection/            # Interaction logging
├── src/core/detection/             # Computer vision modules
│   ├── vision/                     # GPT-4V integration
│   └── sam2_module_fixed.py        # SAM integration
├── benchmarking/                   # Cognitive assessment
│   ├── graph_ml_benchmarking.py   # GNN analysis
│   ├── linkography_*.py            # Linkography modules
│   └── benchmark_dashboard.py      # Interactive dashboard
└── knowledge_base/                 # Architectural knowledge
    └── downloaded_pdfs/            # 40+ architecture texts
```

---

## 📈 Data Collection & Analysis

### Automatic Logging
- Every interaction is automatically logged to CSV files
- Session data includes timestamps, metrics, and full conversation history
- Export button in sidebar for manual data export

### Data Format
```
thesis_data/
├── interactions_[session_id].csv   # Detailed interaction logs
├── full_log_[session_id].json     # Complete session data
└── session_summary_[session_id].json  # Summary metrics
```

---

## 🧪 Testing & Validation

### B-Test Framework
- Comprehensive testing suite for architectural education scenarios
- Validates cognitive enhancement effectiveness
- Measures improvement over traditional tutoring methods

### Performance Requirements
- Real-time response: <100ms for linkograph updates
- Scalability: 100+ concurrent sessions
- Accuracy: >80% correlation with human assessments

---

## 🔧 Configuration

### Environment Variables (.env)
```
OPENAI_API_KEY=your_openai_api_key
SAM_DEVICE=cpu  # or cuda for GPU
```

### Config Files
- `config.json`: Main application settings
- `benchmarking/config/`: Benchmarking-specific settings

---

## 📚 Research Components

### Thesis Objectives
1. **Prevent Cognitive Offloading**: Encourage deep thinking over quick answers
2. **Enhance Critical Thinking**: Socratic method implementation
3. **Track Learning Progress**: Real-time cognitive assessment
4. **Visualize Design Thinking**: Linkography integration

### Publications & References
- Based on Gabriela Goldschmidt's Linkography methodology
- Implements cognitive load theory principles
- Follows educational scaffolding best practices

---

## 🤝 Contributing

This is an active thesis project. For questions or collaboration:
- Review `CLAUDE.md` for detailed development guidelines
- Check `thesis_docs/` for research documentation
- Run tests before submitting changes

---

## 📄 License

This project is part of the MaCAD (Master in Advanced Computation for Architecture & Design) thesis program.

---

**Built with ❤️ for the future of architectural education**