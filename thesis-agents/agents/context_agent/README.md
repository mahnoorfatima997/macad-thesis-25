# Context Agent - Modular Architecture

The Context Agent has been refactored into a clean, modular structure while maintaining full backward compatibility with the original implementation.

## 📁 Package Structure

```
context_agent/
├── __init__.py           # Package initialization and exports
├── adapter.py            # Main adapter maintaining backward compatibility
├── config.py             # Configuration constants and patterns
├── schemas.py            # Typed data models and schemas
└── README.md            # This documentation
```

## 🎯 Core Functionality

The Context Agent provides:
- **Student Input Analysis**: Classifies interaction types and understanding levels
- **Conversation Pattern Analysis**: Tracks engagement and learning progression
- **Routing Suggestions**: Recommends appropriate agents for student needs
- **Cognitive State Assessment**: Evaluates confidence, engagement, and understanding
- **Context Quality Scoring**: Measures the richness of conversational context

## 🔧 Key Components

### Configuration (`config.py`)
- **Analysis Patterns**: Linguistic patterns for different interaction types
- **Technical Terms**: Architectural vocabulary for complexity assessment
- **Emotional Indicators**: Patterns for engagement and mood detection
- **Design Phase Indicators**: Keywords for identifying design phase
- **Complexity Thresholds**: Scoring thresholds for various metrics

### Schemas (`schemas.py`)
- **InteractionType**: Enumerated student interaction classifications
- **UnderstandingLevel**: Student comprehension levels
- **ConfidenceLevel**: Student confidence states
- **EngagementLevel**: Student participation levels
- **ContextPackage**: Complete context analysis result
- **RoutingSuggestions**: Agent routing recommendations

## 🔄 Backward Compatibility

The original `ContextAgent` class interface is preserved:

```python
from agents.context_agent import ContextAgent

# Original usage still works exactly the same
agent = ContextAgent("architecture")
context = await agent.analyze_student_input(state, current_input)
```

## 🚀 Usage

### Basic Usage
```python
from agents.context_agent import ContextAgent

agent = ContextAgent()
analysis = await agent.analyze_student_input(state, user_input)
```

### Advanced Usage
```python
# Access typed schemas
from agents.context_agent.schemas import ContextPackage, InteractionType

# Use configuration directly
from agents.context_agent.config import ANALYSIS_PATTERNS, TECHNICAL_TERMS
```

## 🎨 Key Features

### Student Input Classification
- **Interaction Types**: Question, statement, exploration, feedback request, confusion
- **Understanding Levels**: Novice, developing, proficient, advanced
- **Confidence Levels**: Low, moderate, high, overconfident
- **Engagement Levels**: Disengaged, passive, active, highly engaged

### Content Analysis
- **Technical Term Extraction**: Identifies architectural vocabulary usage
- **Complexity Scoring**: Measures input sophistication
- **Emotional Indicators**: Detects enthusiasm, confusion, frustration
- **Specificity Assessment**: Evaluates project-specific content

### Conversation Pattern Analysis
- **Topic Tracking**: Monitors conversation focus areas
- **Engagement Trends**: Tracks participation over time
- **Understanding Progression**: Measures learning development
- **Repetitive Pattern Detection**: Identifies stuck or circular discussions

### Routing Intelligence
- **Agent Recommendations**: Suggests most appropriate agents
- **Confidence Scoring**: Provides routing certainty metrics
- **Priority Weighting**: Ranks agent suitability
- **Context Packaging**: Prepares agent-specific context

## 🧠 Cognitive Insights

The Context Agent provides deep insights into student learning:

### Learning State Detection
- **Cognitive Load Assessment**: Identifies overwhelm or under-challenge
- **Metacognitive Awareness**: Measures self-reflection capabilities
- **Knowledge Integration**: Evaluates concept connection abilities
- **Learning Progression**: Tracks skill development over time

### Pedagogical Opportunities
- **Socratic Questioning**: When to ask probing questions
- **Knowledge Building**: When to provide information
- **Challenge Introduction**: When to increase difficulty
- **Scaffolding Provision**: When to provide support

## 📊 Integration

The Context Agent is central to the multi-agent system:
- **Orchestrator**: Provides routing decisions and context
- **Socratic Tutor**: Receives context for question targeting
- **Domain Expert**: Gets context for knowledge relevance
- **Cognitive Enhancement**: Uses context for challenge selection
- **Analysis Agent**: Receives context for assessment focus

## 🔍 Analysis Capabilities

### Real-time Assessment
- **Immediate Classification**: Instant input categorization
- **Dynamic Adaptation**: Context-aware response adjustment
- **Quality Validation**: Context analysis verification
- **Confidence Tracking**: Analysis certainty measurement

### Longitudinal Tracking
- **Conversation History**: Long-term pattern analysis
- **Learning Trajectory**: Progress over multiple sessions
- **Skill Development**: Competency growth tracking
- **Engagement Evolution**: Participation change monitoring

## 🔧 Development

### Adding New Patterns
1. Update pattern dictionaries in `config.py`
2. Extend classification logic in `adapter.py`
3. Add corresponding schema types if needed
4. Update routing logic for new classifications

### Enhancing Analysis
1. Add new metrics to schemas
2. Implement calculation methods in adapter
3. Update context package structure
4. Extend agent-specific context preparation

## 🚀 Future Enhancements

- **Machine Learning Integration**: Automated pattern learning
- **Multi-modal Analysis**: Image and voice input processing
- **Predictive Modeling**: Anticipating student needs
- **Personalization**: Individual learning style adaptation
- **Real-time Feedback**: Live coaching suggestions 