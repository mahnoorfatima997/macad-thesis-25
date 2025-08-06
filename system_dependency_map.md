# System Dependency Map - Thesis Agents

## Core System Architecture

```
mega_architectural_mentor.py (Main Interface)
├── thesis-agents/
│   ├── agents/
│   │   ├── analysis_agent.py
│   │   ├── cognitive_enhancement.py
│   │   ├── context_agent.py
│   │   ├── domain_expert.py
│   │   └── socratic_tutor.py
│   ├── orchestration/
│   │   └── langgraph_orchestrator.py
│   ├── data_collection/
│   │   └── interaction_logger.py
│   ├── knowledge_base/
│   │   └── knowledge_manager.py
│   ├── phase_management/
│   │   ├── milestone_questions.py
│   │   └── progress_manager.py
│   ├── state_manager.py
│   ├── conversation_progression.py
│   └── first_response_generator.py
```

## Agent Dependencies

### AnalysisAgent Dependencies
- **Imports**: SketchAnalyzer, KnowledgeManager, MilestoneType
- **Dependencies**: state_manager, vision.sketch_analyzer, knowledge_base.knowledge_manager
- **Outputs**: analysis_result, phase_detection, cognitive_flags

### CognitiveEnhancementAgent Dependencies
- **Imports**: OpenAI, numpy, math
- **Dependencies**: state_manager
- **Outputs**: cognitive_challenge, scientific_metrics, enhancement_strategy

### ContextAgent Dependencies
- **Imports**: OpenAI, re
- **Dependencies**: state_manager
- **Outputs**: context_classification, routing_suggestions, cognitive_offloading_detection

### DomainExpertAgent Dependencies
- **Imports**: OpenAI, requests, json
- **Dependencies**: state_manager, knowledge_base.knowledge_manager
- **Outputs**: knowledge_results, examples, technical_knowledge

### SocraticTutorAgent Dependencies
- **Imports**: OpenAI, random
- **Dependencies**: state_manager
- **Outputs**: socratic_question, educational_intent, response_strategy

### LangGraphOrchestrator Dependencies
- **Imports**: LangGraph, all agents
- **Dependencies**: All agents, state_manager, conversation_progression
- **Outputs**: final_response, routing_decision, agent_coordination

## Data Flow Analysis

### Primary Data Flow
1. **User Input** → ContextAgent (classification)
2. **ContextAgent** → Router (routing decision)
3. **Router** → AnalysisAgent (if needed)
4. **AnalysisAgent** → DomainExpert (if knowledge needed)
5. **DomainExpert** → SocraticTutor (if questioning needed)
6. **SocraticTutor** → CognitiveEnhancement (if challenge needed)
7. **All Agents** → Synthesizer (final response)

### State Management Flow
1. **ArchMentorState** → All agents (shared state)
2. **Agent Results** → State updates
3. **State Updates** → InteractionLogger
4. **InteractionLogger** → Data collection for thesis

## Communication Patterns

### Agent-to-Agent Communication
- **ContextAgent** → **Router**: Classification results
- **Router** → **AnalysisAgent**: Analysis requests
- **AnalysisAgent** → **DomainExpert**: Knowledge requests
- **DomainExpert** → **SocraticTutor**: Example-based questions
- **SocraticTutor** → **CognitiveEnhancement**: Challenge requests

### State Sharing
- **ArchMentorState**: Central state shared by all agents
- **Agent Context**: Individual agent context packages
- **Metadata**: Response metadata for logging

## Critical Dependencies

### High-Priority Dependencies
1. **OpenAI API**: All agents depend on OpenAI for responses
2. **State Manager**: All agents depend on ArchMentorState
3. **LangGraph Orchestrator**: Controls all agent coordination
4. **Interaction Logger**: Captures all interactions for thesis

### Medium-Priority Dependencies
1. **Knowledge Manager**: DomainExpert depends on knowledge base
2. **Sketch Analyzer**: AnalysisAgent depends on visual analysis
3. **Conversation Progression**: Orchestrator depends on progression management

### Low-Priority Dependencies
1. **Configuration files**: Development and orchestrator configs
2. **Utility modules**: Response length controller, etc.

## Bottlenecks Identified

### Performance Bottlenecks
1. **Multiple OpenAI API calls**: Each agent makes separate API calls
2. **Sequential processing**: Agents process in sequence, not parallel
3. **State updates**: Frequent state updates may cause delays

### Coordination Bottlenecks
1. **Complex routing logic**: Lines 433-554 in orchestrator
2. **Agent communication**: No standardized communication protocol
3. **Response synthesis**: Manual synthesis in orchestrator

### Data Flow Bottlenecks
1. **State management**: No validation of state updates
2. **Logging complexity**: Complex interaction logging structure
3. **Error handling**: Limited error handling across agents

## Optimization Opportunities

### Immediate Optimizations
1. **Reduce API calls**: Cache responses and reuse across agents
2. **Parallel processing**: Process independent agents in parallel
3. **Standardize communication**: Create standard agent response format

### Medium-term Optimizations
1. **Simplify routing**: Reduce routing decision complexity
2. **Enhance state management**: Add validation and error handling
3. **Optimize logging**: Simplify interaction logger structure

### Long-term Optimizations
1. **Agent specialization**: Further specialize agent responsibilities
2. **Intelligent caching**: Implement smart caching strategies
3. **Performance monitoring**: Add comprehensive monitoring

## Unused/Redundant Code

### Potential Dead Code
1. **Test functions**: Many test functions in agent files
2. **Fallback methods**: Unused fallback methods
3. **Configuration options**: Unused configuration parameters

### Duplicate Functionality
1. **Phase detection**: Multiple agents have phase detection logic
2. **Classification**: Context and analysis agents both classify input
3. **Response generation**: Multiple agents generate responses

## Recommendations

### Week 1 Priorities
1. **Audit all imports**: Remove unused imports
2. **Simplify routing**: Reduce orchestrator complexity
3. **Standardize responses**: Create standard agent response format
4. **Add validation**: Add state and data validation

### Week 2 Priorities
1. **Optimize API calls**: Implement caching and parallel processing
2. **Enhance coordination**: Improve agent communication
3. **Add error handling**: Comprehensive error handling across system

### Week 3 Priorities
1. **Performance monitoring**: Add performance metrics
2. **Code cleanup**: Remove dead code and duplicates
3. **Documentation**: Complete system documentation 