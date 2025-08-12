# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Multi-Agent AI Educational System** (thesis-agents) that implements cognitive enhancement for architecture students. The system uses LangGraph orchestration to coordinate multiple specialized AI agents that provide knowledge, ask Socratic questions, and challenge assumptions without encouraging cognitive offloading.

## Common Development Commands

### Running the Application
```bash
# Main Streamlit interface
python -c "import streamlit as st; st.run('app.py')"
# or if streamlit CLI is available:
streamlit run app.py
```

### Testing
```bash
# Run individual test files
python test_analysis_agent.py
python test_socratic.py
python test_classification.py
python test_vision.py
python test_state.py

# Test knowledge base functionality
python test_knowledge_content.py
python test_debug_knowledge_search.py
python test_rebuild_knowledge_base.py

# Test orchestration
python test_synthesizer.py
```

### Knowledge Base Management
```bash
# Rebuild vector database
python test_rebuild_knowledge_base.py

# Debug knowledge search
python test_debug_knowledge_search.py
python test_debug_embeddings.py
```

### Dependencies
```bash
# Install all requirements
pip install -r requirements.txt

# Key dependencies: openai, langchain, langgraph, chromadb, streamlit, fastapi
```

## Architecture Overview

### Multi-Agent System Structure

**Core Agents** (in `agents/`):
- **AnalysisAgent** (`analysis_agent.py`): Dynamic skill assessment, visual analysis, cognitive flag generation
- **SocraticTutorAgent** (`socratic_tutor.py`): AI-powered adaptive questioning system  
- **DomainExpertAgent** (`domain_expert.py`): Multi-strategy knowledge discovery and synthesis
- **CognitiveEnhancementAgent** (`cognitive_enhancement.py`): Cognitive challenges and metacognitive development
- **ContextAgent** (`context_agent.py`): Context reasoning and routing preparation

**Orchestration System** (`orchestration/`):
- **LangGraphOrchestrator** (`langgraph_orchestrator.py`): LangGraph-based workflow coordination with AI-powered routing
- Uses `WorkflowState` for information flow between agents
- Implements sophisticated routing based on student learning state classification

**Knowledge System** (`knowledge_base/`):
- **KnowledgeManager** (`knowledge_manager.py`): ChromaDB-based vector knowledge base
- Processes PDFs from `downloaded_pdfs/` directory
- Maintains vectorstore in `vectorstore/` with chroma.sqlite3

**State Management** (`state_manager.py`):
- **ArchMentorState**: Central state container for conversation and student context
- **StudentProfile**: Dynamic skill level and learning state tracking
- **VisualArtifact**: Image analysis results and annotations

### Workflow Execution

1. **Student Input** → **ContextAgent** (AI-powered classification)
2. **Router** determines path: `knowledge_only`, `socratic_focus`, `cognitive_challenge`, `multi_agent`, or `default`
3. **Agent Execution** through appropriate agents based on routing
4. **Synthesizer** combines outputs with pedagogical priority ordering
5. **Response Generation** with metadata and routing information

### Key Routing Paths

- **knowledge_only**: Technical questions + high understanding → Domain Expert only
- **socratic_focus**: Confusion or low understanding → Analysis + Socratic focus
- **cognitive_challenge**: Overconfidence → Analysis + Cognitive challenges
- **multi_agent**: Feedback requests → Full agent coordination
- **default**: Standard interactions → Knowledge + Socratic guidance

## Key System Features

### AI-Powered Analysis
- **Skill Assessment**: Real-time detection based on vocabulary and complexity
- **Visual Analysis**: Computer vision analysis of architectural sketches  
- **Context Classification**: GPT-4 powered learning state detection
- **Cognitive Flags**: AI-generated indicators for pedagogical interventions

### Knowledge Integration
- **Vector Search**: ChromaDB-based semantic search of architectural knowledge
- **Multi-Strategy Discovery**: Conceptual, analogical, decomposition, cross-domain approaches
- **Web Search Fallback**: Integration when local knowledge insufficient
- **Source Synthesis**: Combines multiple knowledge sources with discovery method awareness

### Educational Features
- **Cognitive Enhancement**: Prevents cognitive offloading through guided discovery
- **Adaptive Questioning**: Dynamic Socratic method based on student state
- **Assumption Challenges**: Context-aware cognitive challenges
- **Thesis Data Collection**: Comprehensive interaction logging for research

## Data Collection System

**Interaction Logging** (`data_collection/interaction_logger.py`):
- Captures cognitive enhancement metrics
- Exports thesis-ready data with session summaries
- Baseline comparison capabilities
- Session metrics tracking

**Thesis Data** (`thesis_data/`):
- Session summaries with cognitive enhancement rates
- Full interaction logs for analysis
- Comparative data against traditional tutoring

## Frontend Integration

**Streamlit Interface** (`app.py`):
- Phase 1: Design analysis with visual upload
- Phase 2: Multi-agent conversation with enhanced debugging
- Real-time cognitive metrics display
- Visual artifact management

**Vision System** (`vision/sketch_analyzer.py`):
- Architectural sketch analysis
- GPT-4V integration for visual understanding
- Element identification and spatial relationship analysis

## Development Notes

### Testing Strategy
- Individual agent testing with dedicated test files
- Integration testing through orchestrator tests
- Knowledge base validation and debugging tools
- Visual analysis testing with sample images

### Configuration
- Domain-specific initialization (architecture/game_design)
- OpenAI API integration throughout system
- ChromaDB persistent storage configuration
- Session state management across Streamlit interface

### Error Handling
- Comprehensive fallback mechanisms in all agents
- Classification confidence validation
- Safe response generation when AI components fail
- Robust routing with default paths for edge cases

## Important Implementation Details

### State Flow
- All agents operate on shared `ArchMentorState`
- Context information flows through `WorkflowState` in LangGraph
- Dynamic skill level updates based on interaction analysis
- Conversation history maintained for context continuity

### Agent Coordination
- Sequential execution: Analysis → Domain → Socratic → Cognitive
- Context-aware agent selection based on student needs
- Priority-based response synthesis (Socratic > Cognitive > Domain)
- Cross-agent information sharing through state objects

### Performance Considerations
- ChromaDB vector operations for knowledge retrieval
- GPT-4 API calls for analysis and generation
- Image processing for visual artifact analysis
- Session state persistence in Streamlit