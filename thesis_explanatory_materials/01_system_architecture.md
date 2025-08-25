# MEGA Architectural Mentor System Architecture

## Executive Summary

The MEGA (Multimodal Educational Guidance for Architecture) system is a sophisticated multi-agent AI orchestration platform designed to enhance architectural design education through intelligent tutoring, cognitive scaffolding, and comprehensive performance analysis. The system combines advanced AI agents, real-time cognitive assessment, linkography analysis, and comprehensive benchmarking to create an adaptive learning environment that prevents cognitive offloading while promoting deep thinking in spatial design.

## System Overview

```mermaid
graph TB
    subgraph "User Interface Layer"
        UI[Dashboard UI<br/>Streamlit]
        WEB[Web Interface]
        MOBILE[Mobile Support]
    end

    subgraph "Core Orchestration Layer"
        ORCH[LangGraph Orchestrator<br/>Multi-Agent Coordination]
        ROUTE[Advanced Routing<br/>Decision Tree]
        STATE[State Management<br/>Session Context]
    end

    subgraph "Multi-Agent System"
        SA[Socratic Tutor<br/>Questioning & Guidance]
        DE[Domain Expert<br/>Knowledge Base Access]
        CE[Cognitive Enhancement<br/>Learning Scaffolding]
        AA[Analysis Agent<br/>Pattern Recognition]
        CA[Context Agent<br/>Conversation Management]
    end

    subgraph "Knowledge & Processing"
        KB[Knowledge Base<br/>RAG System (ChromaDB)]
        VISION[Vision System<br/>Image Analysis & Generation]
        NLP[NLP Pipeline<br/>Text Processing]
    end

    subgraph "Testing & Assessment"
        TEST[Thesis Tests<br/>Controlled Experiments]
        CTRL[Control Groups<br/>MENTOR/GenericAI/NoAI]
        LINK[Linkography Engine<br/>Design Move Analysis]
    end

    subgraph "Data Collection & Storage"
        DATA[Thesis Data<br/>Session Interactions]
        METRICS[Cognitive Metrics<br/>Real-time Assessment]
        MOVES[Design Moves<br/>Linkographic Data]
    end

    subgraph "Analysis & Benchmarking"
        BENCH[Benchmarking Suite<br/>Performance Analysis]
        GRAPH[Graph ML Pipeline<br/>Pattern Recognition]
        VIZ[Visualization Engine<br/>Interactive Reports]
    end

    UI --> ORCH
    ORCH --> SA
    ORCH --> DE  
    ORCH --> CE
    ORCH --> AA
    ORCH --> CA
    
    ORCH --> ROUTE
    ORCH --> STATE
    
    DE --> KB
    CA --> VISION
    AA --> NLP
    
    UI --> TEST
    TEST --> CTRL
    TEST --> LINK
    
    ORCH --> DATA
    DATA --> METRICS
    DATA --> MOVES
    
    DATA --> BENCH
    BENCH --> GRAPH
    BENCH --> VIZ
    
    KB --> VISION
    LINK --> MOVES
    GRAPH --> VIZ
```

## Component Architecture Deep Dive

### 1. Multi-Agent Orchestration System (`thesis-agents/`)

The heart of the system is a sophisticated multi-agent orchestration platform built on LangGraph, providing intelligent coordination between specialized AI agents.

#### Core Orchestration (`orchestration/orchestrator.py`)
- **LangGraphOrchestrator**: Central coordinator managing agent interactions
- **Advanced Routing System**: Context-aware decision tree for agent selection
- **State Management**: Comprehensive session and conversation state tracking
- **Synthesis Engine**: Intelligent response combination from multiple agents

#### Specialized Agents (`agents/`)
Each agent serves a specific pedagogical function:

**Socratic Tutor Agent** (`socratic_tutor.py`)
- Primary function: Socratic questioning and guided discovery
- Prevents cognitive offloading by never providing direct answers
- Scaffolds learning through strategic questioning
- Promotes metacognitive awareness

**Domain Expert Agent** (`domain_expert.py`)
- Access to comprehensive architectural knowledge base
- Provides contextual information and examples
- Supports technical queries and reference material
- Maintains citation tracking for academic integrity

**Cognitive Enhancement Agent** (`cognitive_enhancement.py`)
- Real-time cognitive load assessment
- Learning progression monitoring
- Personalized scaffolding strategies
- Gamification and engagement optimization

**Analysis Agent** (`analysis_agent.py`)
- Conversation pattern recognition
- Phase detection and progression tracking
- User engagement and understanding assessment
- Educational effectiveness measurement

**Context Agent** (`context_agent.py`)
- Conversation continuity management
- Topic transition detection
- Building type and project context extraction
- Multi-modal content integration

### 2. Knowledge Base & RAG System (`knowledge_base/`)

A sophisticated Retrieval-Augmented Generation (RAG) system providing contextual architectural knowledge.

#### Knowledge Management (`knowledge_manager.py`)
- **ChromaDB Integration**: Vector database for semantic search
- **PDF Processing**: Automated document ingestion and chunking
- **Citation Management**: Academic referencing and source tracking
- **Multi-modal Support**: Text, image, and document processing

#### Content Structure
- **Raw Documents**: PDF repository for architectural resources
- **Vector Store**: Semantic embeddings for efficient retrieval
- **Citation Database**: Metadata and reference information
- **Query Interface**: Semantic search with relevance scoring

### 3. Testing Framework (`thesis_tests/`)

Comprehensive testing environment for controlled educational research.

#### Test Environments
**MENTOR Group**: Full multi-agent system with cognitive scaffolding
- Socratic questioning approach
- Prevents direct answer provision
- Promotes deep thinking and reflection
- Expected high cognitive engagement scores

**Generic AI Group**: Traditional AI assistant approach
- Direct question answering
- Provides solutions and examples
- Conventional tutoring methods
- Baseline comparison for effectiveness

**Control Group**: No AI assistance
- Traditional resources only
- Self-directed learning
- Natural cognitive processes
- Pure baseline measurement

#### Data Collection (`data_models.py`, `enhanced_data_collector.py`)
- **Interaction Logging**: Complete conversation capture
- **Move Parsing**: Design move extraction and classification
- **Cognitive Metrics**: Real-time assessment of learning indicators
- **Session Metadata**: Comprehensive context tracking

### 4. Linkography Engine (`thesis_tests/linkography_*.py`)

Implementation of Gabriela Goldschmidt's linkography methodology for design process analysis.

#### Core Components
**Move Classification**:
- Move types: analysis, synthesis, evaluation, transformation, reflection
- Design phases: ideation, visualization, materialization
- Cognitive operations: proposal, clarification, assessment, support
- Design focus: function, form, structure, material, environment, culture

**Link Generation**:
- Semantic similarity using sentence transformers
- Temporal relationship analysis
- Fuzzy link strength calculation (0.35 threshold)
- Pattern detection (chunks, webs, sawteeth)

**Cognitive Mapping**:
- Links linkography patterns to cognitive metrics
- Identifies design fixation, breakthrough moments, and overload
- Tracks creative progression and problem-solving strategies

### 5. Data Flow & Storage (`thesis_data/`)

Centralized data management for all system interactions and analysis.

#### Data Types
- **Interactions**: User-system conversation logs
- **Design Moves**: Linkographic analysis data
- **Metrics**: Cognitive assessment measurements
- **Sessions**: Complete session metadata and context
- **Generated Images**: AI-created visualizations and metadata
- **Linkography**: Design process visualizations and patterns

#### Storage Structure
```
thesis_data/
├── interactions_[session_id].csv      # User-system interactions
├── design_moves_[session_id].csv      # Linkographic moves
├── metrics_[session_id].csv           # Cognitive measurements
├── session_[session_id].json          # Complete session data
├── linkography/                       # Design process analysis
│   ├── linkography_[session_id].json
│   └── linkography_moves_[session_id].jsonl
└── generated_images/                  # AI visualizations
    ├── [timestamp]_visualization.png
    └── [timestamp]_metadata.json
```

### 6. Benchmarking & Analysis System (`benchmarking/`)

Comprehensive performance evaluation and research analysis platform.

#### Core Analysis Components
**Graph ML Pipeline** (`graph_ml_benchmarking.py`)
- Converts interactions to graph structures
- Graph Neural Network (GNN) pattern analysis
- Cognitive proficiency clustering
- Comparative effectiveness measurement

**Evaluation Metrics** (`evaluation_metrics.py`)
- Six core cognitive metrics:
  1. Cognitive Offloading Prevention (COP)
  2. Deep Thinking Engagement (DTE)
  3. Scaffolding Effectiveness (SE)
  4. Knowledge Integration (KI)
  5. Learning Progression (LP)
  6. Metacognitive Awareness (MA)

**Linkography Integration** (`linkography_*.py`)
- Design process visualization
- Pattern recognition and analysis
- Cognitive load assessment
- Creative breakthrough detection

#### Visualization & Reporting
**Interactive Dashboards**:
- Proficiency analysis and clustering
- Agent effectiveness comparisons
- Learning progression tracking
- Cognitive pattern visualization

**Research Reports**:
- Comprehensive benchmarking analysis
- Educational effectiveness assessment
- Comparative group analysis
- Statistical significance testing

## Data Pipeline Flow

### Primary Data Flow
1. **User Interaction** → Dashboard UI captures input
2. **Orchestration** → LangGraph routes to appropriate agents
3. **Agent Processing** → Specialized agents generate responses
4. **Synthesis** → Orchestrator combines and shapes final response
5. **Data Logging** → All interactions logged to thesis_data/
6. **Real-time Analysis** → Cognitive metrics calculated and stored
7. **Linkography Generation** → Design moves extracted and linked
8. **Benchmarking** → Performance evaluation and visualization

### Secondary Analysis Flow
1. **Data Collection** → Batch processing of session data
2. **Graph ML Processing** → Interaction patterns to graph structures
3. **Cognitive Assessment** → Metric calculation and proficiency classification
4. **Linkography Analysis** → Design process visualization
5. **Comparative Analysis** → Multi-group effectiveness evaluation
6. **Visualization Generation** → Interactive reports and dashboards
7. **Research Export** → Academic reporting and publication

## Key Architectural Decisions & Rationale

### 1. Multi-Agent Architecture
**Decision**: Specialized agents rather than monolithic AI
**Rationale**: 
- Enables precise pedagogical control
- Allows individual agent optimization
- Supports cognitive scaffolding strategies
- Facilitates research on agent effectiveness

### 2. LangGraph Orchestration
**Decision**: Graph-based workflow management
**Rationale**:
- Provides deterministic agent coordination
- Enables complex conversational flows
- Supports state management across interactions
- Allows for sophisticated routing logic

### 3. Real-time Linkography
**Decision**: Live design move analysis during interaction
**Rationale**:
- Enables immediate cognitive feedback
- Supports adaptive tutoring strategies
- Provides research data without post-processing delay
- Allows for intervention during cognitive overload

### 4. Semantic Embeddings for Knowledge Retrieval
**Decision**: Vector-based knowledge search using ChromaDB
**Rationale**:
- Provides contextually relevant information
- Supports semantic rather than keyword matching
- Enables efficient similarity search
- Maintains citation tracking for academic use

### 5. Three-Group Testing Framework
**Decision**: MENTOR vs Generic AI vs Control comparison
**Rationale**:
- Establishes clear effectiveness baselines
- Isolates multi-agent system benefits
- Provides statistical validity for research
- Enables publication-quality research outcomes

### 6. Modular Dashboard Architecture
**Decision**: Component-based UI with clear separation
**Rationale**:
- Supports multiple testing modes
- Enables rapid feature development
- Facilitates maintenance and updates
- Allows for research-specific customizations

## Integration Points

### External Dependencies
- **OpenAI API**: GPT-4 for agent reasoning and responses
- **Replicate API**: Image generation and analysis
- **ChromaDB**: Vector database for knowledge management
- **Streamlit**: Web interface framework
- **PyTorch**: Machine learning pipeline support

### Internal Module Communication
- **Session State**: Shared context across all components
- **Event System**: Real-time updates between UI and processing
- **Data Pipelines**: Standardized data flow between components
- **API Interfaces**: Consistent interfaces between major systems

## Performance & Scalability Considerations

### Current Capacity
- **Concurrent Users**: Single-user sessions (research prototype)
- **Data Storage**: Local file system with structured organization
- **Processing Load**: Real-time response generation and analysis
- **Session Length**: Extended interactions (2+ hours) supported

### Scalability Pathways
- **Multi-user Support**: Database migration for concurrent access
- **Cloud Deployment**: Containerized architecture for cloud hosting
- **Data Warehousing**: Migration to enterprise database systems
- **Load Balancing**: Distributed agent processing for higher throughput

## Security & Privacy

### Data Protection
- **Local Storage**: All data remains on local system
- **Session Isolation**: Complete separation between user sessions
- **API Security**: Secure key management for external services
- **Data Anonymization**: Personal identifiers removed from research data

### Research Ethics
- **Informed Consent**: Clear explanation of data collection
- **Data Minimization**: Only necessary data collected and stored
- **Participant Rights**: Full data access and deletion capabilities
- **Institutional Oversight**: Aligned with research ethics guidelines

## Future Development Pathways

### Short-term Enhancements
- **Advanced Vision Integration**: Enhanced image analysis and generation
- **Multi-language Support**: Internationalization for global research
- **Mobile Interface**: Responsive design for tablet/mobile use
- **Real-time Collaboration**: Multi-user design session support

### Long-term Research Extensions
- **VR/AR Integration**: Spatial design in immersive environments
- **Advanced AI Models**: Integration of newer foundation models
- **Longitudinal Studies**: Extended learning progression tracking
- **Cross-cultural Analysis**: Comparative education research across cultures

### Technical Architecture Evolution
- **Microservices Migration**: Independent service deployment
- **GraphQL API**: Unified data access layer
- **Real-time Streaming**: Live collaboration and feedback
- **Advanced Analytics**: Predictive modeling for learning outcomes

## Conclusion

The MEGA Architectural Mentor system represents a sophisticated integration of educational theory, advanced AI orchestration, and rigorous research methodology. Its modular architecture supports both immediate educational applications and extensive research analysis, while maintaining the flexibility needed for ongoing development and adaptation.

The system's strength lies in its comprehensive approach to architectural education, combining proven pedagogical methods (Socratic tutoring, cognitive scaffolding) with cutting-edge AI capabilities (multi-agent orchestration, real-time linkography) and robust research infrastructure (controlled testing, comprehensive benchmarking).

This architecture provides a solid foundation for advancing our understanding of AI-enhanced spatial design education while delivering practical benefits to students and educators in the architectural design process.

---

*Document prepared as part of the MaCAD Thesis project: "Multimodal AI Systems for Professional Spatial Design Workflows"*  
*Institute for Advanced Architecture of Catalonia, 2025*