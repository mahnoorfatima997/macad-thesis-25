# Conversation Testing Tools for Mega Architectural Mentor

This directory contains RAG-based conversation testing tools to debug and validate the conversation flows in `mega_architectural_mentor.py` without using the Streamlit interface.

## Overview

The testing tools provide three different approaches for debugging conversation flows:

1. **RAG Conversation Tester** (`rag_conversation_tester.py`) - Comprehensive testing with multiple personas
2. **Quick Conversation Debugger** (`quick_conversation_debugger.py`) - Simple interactive testing
3. **Batch Conversation Tester** (`batch_conversation_tester.py`) - Automated test scenarios

## Prerequisites

1. **OpenAI API Key**: The tools will automatically load your API key from:
   - A `.env` file in the project root with: `OPENAI_API_KEY="your-api-key-here"`
   - Or from environment variable: `OPENAI_API_KEY`
   
   **Recommended**: Create a `.env` file in your project root:
   ```
   OPENAI_API_KEY="your-actual-api-key-here"
   ```

2. **Dependencies**: Ensure all thesis-agents dependencies are installed:
   ```bash
   pip install -r requirements_mega.txt
   ```

## Quick Start

### 1. Quick Conversation Debugger (Recommended for quick testing)

This is the simplest tool for immediate debugging:

```bash
python quick_conversation_debugger.py
```

**Features:**
- Interactive conversation testing
- Real-time response validation
- Built-in commands (`help`, `state`, `clear`, `quit`)
- Sample questions for quick validation

**Usage:**
1. Run the script
2. Choose test mode (1-3)
3. For interactive mode, type messages and see responses
4. Use `help` to see available commands

### 2. Batch Conversation Tester (Recommended for systematic testing)

This tool runs predefined test scenarios:

```bash
python batch_conversation_tester.py
```

**Features:**
- 5 predefined test scenarios covering different aspects
- Automated validation of expected agents and response types
- Detailed performance metrics
- JSON result export

**Test Scenarios:**
1. **Basic Architecture Questions** - Fundamental concepts
2. **Technical Design Questions** - Advanced design principles
3. **Advanced Concepts** - Research and theoretical topics
4. **Software and Tools** - Technical implementation
5. **Project Feedback** - Critique and analysis

### 3. RAG Conversation Tester (Comprehensive testing)

This tool provides the most comprehensive testing capabilities:

```bash
python rag_conversation_tester.py
```

**Features:**
- Multiple user personas (beginner, intermediate, advanced, professional)
- Detailed conversation analysis
- Performance benchmarking across personas
- Comprehensive logging and result export

## Testing Modes

### Interactive Testing
```bash
# Start interactive session
python quick_conversation_debugger.py
# Choose option 1
```

**Available Commands:**
- `help` - Show available commands
- `state` - Show current conversation state
- `clear` - Clear conversation history
- `quit` - Exit the session

### Sample Questions Testing
```bash
# Run with sample questions
python quick_conversation_debugger.py
# Choose option 2
```

### Custom Conversation Testing
```bash
# Run with your own questions
python quick_conversation_debugger.py
# Choose option 3
```

### Batch Scenario Testing
```bash
# Run all predefined scenarios
python batch_conversation_tester.py
# Choose option 1
```

## Understanding Results

### Success Metrics
- **Success Rate**: Percentage of successful message exchanges
- **Confidence Score**: Average confidence of responses
- **Agent Usage**: Which agents were used in responses
- **Response Types**: Types of responses generated

### Expected Behaviors
- **Beginner Students**: Should get educational, guidance responses
- **Intermediate Students**: Should get analysis and detailed feedback
- **Advanced Students**: Should get theoretical and research insights
- **Professionals**: Should get peer-level discussions

### Common Issues to Check
1. **No Response**: Check API key and network connectivity
2. **Generic Responses**: May indicate agent routing issues
3. **Error Messages**: Check orchestrator initialization
4. **Slow Responses**: May indicate complex agent chains

## Debugging Tips

### 1. Check API Key
```bash
# Check if .env file exists and has the API key
cat .env | grep OPENAI_API_KEY

# Or check environment variable
echo $env:OPENAI_API_KEY  # Windows
echo $OPENAI_API_KEY       # Linux/Mac
```

### 2. Verify Dependencies
```bash
python -c "from thesis-agents.orchestration.langgraph_orchestrator import LangGraphOrchestrator; print('✅ Dependencies OK')"
```

### 3. Test Single Message
```bash
python quick_conversation_debugger.py
# Choose option 3 and enter: "What is sustainable design?"
```

### 4. Check Logs
All tools create detailed logs:
- `rag_conversation_test.log` - RAG tester logs
- Console output - Real-time debugging info

## Result Files

Test results are saved in the `results/` directory:
- `rag_test_results_YYYYMMDD_HHMMSS.json`
- `batch_test_results_YYYYMMDD_HHMMSS.json`

**Result Structure:**
```json
{
  "timestamp": "2024-01-01T12:00:00",
  "scenarios": {
    "scenario_name": {
      "messages": [...],
      "summary": {
        "success_rate": 0.8,
        "average_confidence": 0.75,
        "unique_agents_used": ["SocraticTutorAgent", "DomainExpertAgent"]
      }
    }
  }
}
```

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```
   ModuleNotFoundError: No module named 'thesis-agents'
   ```
   **Solution**: Ensure you're in the correct directory and thesis-agents is available

2. **API Key Issues**
   ```
   ❌ OpenAI API key not found
   ```
   **Solution**: Ensure you have a `.env` file with `OPENAI_API_KEY="your-key"` or set the environment variable

3. **Orchestrator Initialization Errors**
   ```
   ❌ Failed to initialize components
   ```
   **Solution**: Check thesis-agents dependencies and configuration

4. **Slow Responses**
   - Check API rate limits
   - Verify network connectivity
   - Consider reducing test complexity

### Performance Optimization

1. **Reduce Test Scope**: Use quick debugger for immediate issues
2. **Limit Message Count**: Start with 2-3 messages per test
3. **Use Specific Scenarios**: Focus on problematic areas
4. **Check Logs**: Monitor for bottlenecks

## Integration with Main System

These tools test the same components used in `mega_architectural_mentor.py`:
- `LangGraphOrchestrator` - Main conversation orchestrator
- `ArchMentorState` - Conversation state management
- `StudentProfile` - User profile management
- Agent components (SocraticTutorAgent, DomainExpertAgent, etc.)

## Next Steps

1. **Start with Quick Debugger**: For immediate issue identification
2. **Use Batch Tester**: For systematic validation
3. **Analyze Results**: Check success rates and agent usage
4. **Fix Issues**: Address problems identified in testing
5. **Re-test**: Validate fixes with the same tools

## Support

If you encounter issues:
1. Check the logs for detailed error messages
2. Verify all dependencies are installed
3. Ensure API key is correctly set
4. Test with simple questions first
5. Check the thesis-agents documentation for component details 