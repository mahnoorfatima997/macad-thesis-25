# 🧪 Comprehensive Mentor Test Suite

A complete testing framework for validating the entire mentor.py application workflow, including routing logic, interaction types, response generation, and gamification triggers.

## 🎯 **What This Test Suite Validates**

### **Core Functionality Testing**
- ✅ **Routing Logic**: All 14 routing paths with priority-based decision making
- ✅ **Response Generation**: Correct response types for different intents
- ✅ **Gamification Integration**: All 4 gamification triggers and activation logic
- ✅ **Building Type Extraction**: Extraction from first message and persistence
- ✅ **Context Persistence**: Conversation state maintenance across exchanges
- ✅ **Multi-Agent Coordination**: Proper agent selection and orchestration

### **Route Coverage Testing**
Tests all routing paths defined in the system:

| Route | Purpose | Test Scenario |
|-------|---------|---------------|
| `progressive_opening` | First message handling | "I'm designing a community center..." |
| `knowledge_only` | Pure knowledge requests | "What is biophilic design?" |
| `socratic_exploration` | Guided exploration | "I'm thinking about how courtyards..." |
| `cognitive_challenge` | Challenge passive responses | "That makes sense" |
| `multi_agent_comprehensive` | Complex evaluations | "What do you think of my design?" |
| `socratic_clarification` | Confusion handling | "I don't understand" |
| `supportive_scaffolding` | Support requests | "I need help with this" |
| `foundational_building` | Basic knowledge | "Can you explain the basics?" |
| `knowledge_with_challenge` | Knowledge + challenge | "Give me examples with challenge" |
| `balanced_guidance` | General guidance | "I need balanced guidance" |

### **Conversation Flow Testing**
Tests realistic multi-turn conversations:

1. **Progressive Opening → Design Guidance with Gamification**
   - Community center warehouse conversion
   - Flexible space adaptation
   - Example requests

2. **Knowledge Request → Project Examples**
   - Library design project
   - Circulation system examples
   - Noise zoning projects

3. **Confusion Expression → Clarification**
   - School outdoor learning spaces
   - Security vs openness balance
   - Clarification requests

4. **Multi-Agent Comprehensive → Evaluation**
   - Hospital healing gardens
   - Nature integration approach
   - Multi-perspective feedback

5. **Cognitive Challenge Triggers**
   - Office flexible workspaces
   - Passive response triggers
   - Challenge escalation

## 🚀 **How to Run the Tests**

### **Prerequisites**
```bash
# Ensure you have the required environment variables
OPENAI_API_KEY=your_openai_api_key
TAVILY_API_KEY=your_tavily_api_key
LANGSMITH_API_KEY=your_langsmith_api_key
```

### **Basic Usage**
```bash
# Run the complete test suite
python comprehensive_mentor_test.py
```

### **What Happens When You Run It**
1. **🧹 Cleanup**: Removes outdated test files automatically
2. **🚀 Initialization**: Sets up orchestrator and state manager
3. **🛤️ Route Coverage**: Tests all individual routing paths
4. **🔄 Conversation Flows**: Tests multi-turn conversation scenarios
5. **⚠️ Edge Cases**: Tests error handling and edge cases
6. **📊 Report Generation**: Creates comprehensive test report
7. **💾 Data Export**: Saves detailed results to JSON file

## 📊 **Test Output and Reporting**

### **Console Output**
```
🧪 Starting Comprehensive Mentor Test Suite
============================================================

🛤️ Testing Route Coverage
   Route Coverage: progressive_opening ✅
   Route Coverage: knowledge_only ✅
   Route Coverage: socratic_exploration ✅
   ...

🔄 Testing conversation: Progressive Opening → Design Guidance
   Message 1: I'm designing a community center in an old...
   Message 2: I'm thinking about how to create flexible...
   ...

📊 COMPREHENSIVE TEST REPORT
============================================================
📈 OVERALL RESULTS:
   Total Tests: 45
   Passed: 42 (93.3%)
   Failed: 3 (6.7%)

🛤️ ROUTE COVERAGE:
   Routes Tested: 10
   Expected Routes: 10
   Coverage: 100.0%

🎮 GAMIFICATION ANALYSIS:
   Gamified Responses: 12
   Gamification Rate: 26.7%

⚡ PERFORMANCE METRICS:
   Average Response Time: 2.34s
   Maximum Response Time: 5.67s
```

### **Detailed JSON Report**
The test suite generates a timestamped JSON report with:
- Complete test results for each scenario
- Routing decisions and reasoning
- Response classifications
- Performance metrics
- Error details for failed tests
- Conversation flow analysis

Example filename: `mentor_test_report_20241218_143022.json`

## 🔍 **What Each Test Validates**

### **Single Interaction Tests**
- ✅ Correct routing path selection
- ✅ Appropriate response type generation
- ✅ Gamification trigger activation
- ✅ Building type extraction accuracy
- ✅ Response time performance
- ✅ Error handling robustness

### **Conversation Flow Tests**
- ✅ Context persistence across turns
- ✅ Building type consistency
- ✅ Routing adaptation based on conversation state
- ✅ Gamification frequency control
- ✅ Multi-agent coordination
- ✅ State management integrity

### **Edge Case Tests**
- ✅ Empty input handling
- ✅ Very short input processing
- ✅ Very long input handling
- ✅ Special character processing
- ✅ Repeated word handling
- ✅ Error recovery mechanisms

## 🛠️ **Customizing Tests**

### **Adding New Test Scenarios**
Modify the `get_test_scenarios()` method to add new conversation flows:

```python
ConversationTest(
    name="Your Test Name",
    description="Description of what this tests",
    messages=["First message", "Second message", "Third message"],
    expected_routes=["progressive_opening", "socratic_exploration", "knowledge_only"],
    expected_building_type="your_building_type",
    expected_gamification=[False, True, False]
)
```

### **Testing Specific Routes**
Modify the `_test_route_coverage()` method to add specific route tests:

```python
("Your test input", "expected_route_name")
```

### **Adding Custom Validations**
Extend the `TestResult` dataclass and modify validation logic in `test_single_interaction()`.

## 📋 **Interpreting Results**

### **Success Criteria**
- ✅ **Route Coverage**: 100% of expected routes tested
- ✅ **Pass Rate**: >90% of tests passing
- ✅ **Gamification Rate**: 20-40% appropriate gamification
- ✅ **Response Time**: <5s average response time
- ✅ **Building Type Accuracy**: Correct extraction and persistence

### **Common Issues and Solutions**
- **Low Pass Rate**: Check API keys and network connectivity
- **Missing Routes**: Verify routing logic implementation
- **High Response Times**: Check API rate limits and system load
- **Gamification Issues**: Review trigger conditions and thresholds
- **Building Type Errors**: Check extraction logic in context agent

## 🔧 **Maintenance and Updates**

This test suite is designed to be the **single source of truth** for testing the mentor system. As the system evolves:

1. **Update test scenarios** to reflect new features
2. **Add new route tests** when routes are added/modified
3. **Adjust success criteria** based on system requirements
4. **Extend validation logic** for new functionality
5. **Update expected behaviors** based on system changes

## 📝 **Notes**

- The test suite automatically cleans up outdated test files on startup
- All tests use the same API keys as the main application
- Test results are saved with timestamps for historical tracking
- The suite is designed for both development and CI/CD integration
- Performance metrics help identify system bottlenecks and optimization opportunities
