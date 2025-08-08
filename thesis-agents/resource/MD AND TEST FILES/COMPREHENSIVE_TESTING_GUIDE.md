# Comprehensive Testing Guide for Architectural Mentor App

## Overview
This guide provides specific conversation examples to test all features of your architectural mentor system. Each test is designed to trigger different aspects of the agent system and verify functionality.

## **System Architecture & Response Types**

### **Routing Decision Tree (AdvancedRoutingDecisionTree)**
The system uses an advanced routing decision tree that classifies user input and routes to appropriate agents:

**Route Types:**
- `progressive_opening` → Synthesizer (First response)
- `topic_transition` → Synthesizer (Topic changes)
- `cognitive_intervention` → Cognitive Enhancement Agent
- `socratic_exploration` → Socratic Tutor Agent
- `design_guidance` → Socratic Tutor Agent
- `multi_agent_comprehensive` → Analysis Agent → Domain Expert → Socratic Tutor
- `knowledge_with_challenge` → Domain Expert Agent
- `socratic_clarification` → Socratic Tutor Agent
- `supportive_scaffolding` → Socratic Tutor Agent
- `cognitive_challenge` → Cognitive Enhancement Agent
- `foundational_building` → Socratic Tutor Agent
- `balanced_guidance` → Analysis Agent
- `knowledge_only` → Domain Expert Agent
- `socratic_focus` → Analysis Agent

### **Response Types (AgentResponse)**
All agents return standardized `AgentResponse` objects with:

**Core Fields:**
- `response_text`: The actual response content
- `response_type`: Type of response (ANALYSIS, GUIDANCE, KNOWLEDGE, CHALLENGE, etc.)
- `cognitive_flags`: Array of cognitive flags (COGNITIVE_OFFLOADING_DETECTED, SCAFFOLDING_PROVIDED, etc.)
- `enhancement_metrics`: Cognitive enhancement scores
- `agent_name`: Which agent generated the response
- `metadata`: Original agent data for backward compatibility

**Enhancement Metrics:**
- `cognitive_offloading_prevention_score`: 0-1
- `deep_thinking_engagement_score`: 0-1
- `knowledge_integration_score`: 0-1
- `scaffolding_effectiveness_score`: 0-1
- `learning_progression_score`: 0-1
- `metacognitive_awareness_score`: 0-1
- `overall_cognitive_score`: 0-1
- `scientific_confidence`: 0-1

### **Conversation Progression Phases**
- `discovery`: Initial exploration and understanding
- `exploration`: Deepening knowledge and analysis
- `synthesis`: Connecting ideas and forming insights
- `application`: Applying knowledge to specific problems
- `reflection`: Evaluating understanding and identifying gaps

### **Expected Response Patterns**

**Cognitive Enhancement Responses:**
- Should detect offloading attempts
- Provide challenges instead of direct answers
- Ask probing questions
- Include cognitive flags: `COGNITIVE_OFFLOADING_DETECTED`

**Socratic Method Responses:**
- Ask questions instead of giving answers
- Guide discovery and learning
- Include cognitive flags: `SCAFFOLDING_PROVIDED`

**Domain Knowledge Responses:**
- Provide architectural knowledge
- Connect to specific project
- Include sources and references
- Include cognitive flags: `KNOWLEDGE_PROVIDED`

**Analysis Responses:**
- Comprehensive skill assessment
- Phase analysis and progress tracking
- Learning recommendations
- Include cognitive flags: `ANALYSIS_COMPLETED`

---

## **Phase 1: Basic System Functionality Tests**

### **Test 1: Initial Project Setup**
**Input:** "I want to design a community center"

**Expected Routing:** `progressive_opening` → Synthesizer

**Expected Response Type:** `GUIDANCE`

**Expected Response Format:**
```json
{
  "response_text": "Welcome to your architectural design journey! I'm here to guide you through designing a community center...",
  "response_type": "GUIDANCE",
  "cognitive_flags": ["SCAFFOLDING_PROVIDED"],
  "agent_name": "synthesizer",
  "enhancement_metrics": {
    "cognitive_offloading_prevention_score": 0.8,
    "deep_thinking_engagement_score": 0.7,
    "learning_progression_score": 0.6
  },
  "conversation_progression": {
    "conversation_phase": "discovery",
    "phase_progress": 0.1
  }
}
```

**Expected Behavior:**
- System should respond with initial guidance
- Should ask about your experience level
- Should start the discovery phase (not ideation)
- Check sidebar for "Analysis" section updates
- Should show "🔍 Discovery" in phase display

### **Test 2: Experience Level Declaration**
**Input:** "I'm a beginner in architecture"

**Expected Routing:** `socratic_exploration` → Socratic Tutor Agent

**Expected Response Type:** `GUIDANCE`

**Expected Response Format:**
```json
{
  "response_text": "Great! As a beginner, we'll take this step by step...",
  "response_type": "GUIDANCE",
  "cognitive_flags": ["SCAFFOLDING_PROVIDED", "BEGINNER_LEVEL_DETECTED"],
  "agent_name": "socratic_tutor",
  "enhancement_metrics": {
    "scaffolding_effectiveness_score": 0.9,
    "deep_thinking_engagement_score": 0.6,
    "learning_progression_score": 0.7
  },
  "conversation_progression": {
    "conversation_phase": "discovery",
    "phase_progress": 0.3
  }
}
```

**Expected Behavior:**
- System should acknowledge your experience level
- Should provide appropriate scaffolding
- Should ask about specific aspects of community center design
- Check "Classification" section in sidebar
- Should show beginner-appropriate guidance

### **Test 3: Project Scope Definition**
**Input:** "I want to create a community center that serves both young people and elderly"

**Expected Routing:** `multi_agent_comprehensive` → Analysis Agent → Domain Expert → Socratic Tutor

**Expected Response Type:** `ANALYSIS`

**Expected Response Format:**
```json
{
  "response_text": "Excellent! A dual-user community center requires careful consideration of accessibility and programming...",
  "response_type": "ANALYSIS",
  "cognitive_flags": ["ANALYSIS_COMPLETED", "COMPLEX_REQUIREMENT_DETECTED"],
  "agent_name": "analysis_agent",
  "enhancement_metrics": {
    "knowledge_integration_score": 0.8,
    "deep_thinking_engagement_score": 0.7,
    "overall_cognitive_score": 0.75
  },
  "conversation_progression": {
    "conversation_phase": "exploration",
    "phase_progress": 0.2
  },
  "metadata": {
    "skill_assessment": {...},
    "visual_analysis": {...},
    "text_analysis": {...},
    "synthesis": {...}
  }
}
```

**Expected Behavior:**
- System should analyze the dual-user requirement
- Should suggest design considerations
- Should ask about site constraints
- Check "Progress Update" section
- Should show "🔬 Exploration" in phase display

---

## **Phase 2: Cognitive Enhancement Tests**

### **Test 4: Cognitive Offloading Detection**
**Input:** "Can you just tell me exactly what to design?"

**Expected Routing:** `cognitive_intervention` → Cognitive Enhancement Agent

**Expected Response Type:** `CHALLENGE`

**Expected Response Format:**
```json
{
  "response_text": "I understand you want a clear answer, but let me ask you something first...",
  "response_type": "CHALLENGE",
  "cognitive_flags": ["COGNITIVE_OFFLOADING_DETECTED", "CHALLENGE_PROVIDED"],
  "agent_name": "cognitive_enhancement",
  "enhancement_metrics": {
    "cognitive_offloading_prevention_score": 0.95,
    "deep_thinking_engagement_score": 0.8,
    "scaffolding_effectiveness_score": 0.7
  },
  "conversation_progression": {
    "conversation_phase": "exploration",
    "phase_progress": 0.4
  }
}
```

**Expected Behavior:**
- System should detect cognitive offloading attempt
- Should provide a challenge instead of direct answer
- Should ask probing questions
- Check for cognitive enhancement flags in sidebar
- Should NOT give direct design instructions

### **Test 5: Deep Thinking Encouragement**
**Input:** "I'm not sure about the layout"

**Expected Routing:** `socratic_clarification` → Socratic Tutor Agent

**Expected Response Type:** `GUIDANCE`

**Expected Response Format:**
```json
{
  "response_text": "What specifically makes you uncertain about the layout? Let's break this down...",
  "response_type": "GUIDANCE",
  "cognitive_flags": ["SCAFFOLDING_PROVIDED", "UNCERTAINTY_DETECTED"],
  "agent_name": "socratic_tutor",
  "enhancement_metrics": {
    "deep_thinking_engagement_score": 0.85,
    "scaffolding_effectiveness_score": 0.8,
    "metacognitive_awareness_score": 0.7
  },
  "conversation_progression": {
    "conversation_phase": "exploration",
    "phase_progress": 0.5
  }
}
```

**Expected Behavior:**
- System should ask "What makes you uncertain?"
- Should encourage you to think through options
- Should provide scaffolding questions
- Should not give direct answers
- Should guide you to identify specific concerns

### **Test 6: Metacognitive Awareness**
**Input:** "I think I need to reconsider the entrance design"

**Expected Routing:** `socratic_exploration` → Socratic Tutor Agent

**Expected Response Type:** `GUIDANCE`

**Expected Response Format:**
```json
{
  "response_text": "That's excellent self-reflection! What led you to reconsider the entrance design?",
  "response_type": "GUIDANCE",
  "cognitive_flags": ["METACOGNITIVE_AWARENESS_DETECTED", "SCAFFOLDING_PROVIDED"],
  "agent_name": "socratic_tutor",
  "enhancement_metrics": {
    "metacognitive_awareness_score": 0.9,
    "deep_thinking_engagement_score": 0.8,
    "learning_progression_score": 0.8
  },
  "conversation_progression": {
    "conversation_phase": "reflection",
    "phase_progress": 0.7
  }
}
```

**Expected Behavior:**
- System should acknowledge your self-reflection
- Should ask about your reasoning process
- Should encourage deeper analysis
- Check for metacognitive awareness metrics
- Should show "🤔 Reflection" in phase display

---

## **Phase 3: Domain Knowledge Tests**

### **Test 7: Architectural Knowledge Request**
**Input:** "What are the key principles for designing accessible spaces?"

**Expected Routing:** `knowledge_with_challenge` → Domain Expert Agent

**Expected Response Type:** `KNOWLEDGE`

**Expected Response Format:**
```json
{
  "response_text": "Great question! The key principles for accessible design include universal design, clear circulation paths...",
  "response_type": "KNOWLEDGE",
  "cognitive_flags": ["KNOWLEDGE_PROVIDED", "DOMAIN_EXPERT_USED"],
  "agent_name": "domain_expert",
  "enhancement_metrics": {
    "knowledge_integration_score": 0.9,
    "deep_thinking_engagement_score": 0.7,
    "learning_progression_score": 0.8
  },
  "conversation_progression": {
    "conversation_phase": "exploration",
    "phase_progress": 0.6
  },
  "metadata": {
    "sources": ["Universal Design Principles", "ADA Guidelines"],
    "domain_knowledge": {...}
  }
}
```

**Expected Behavior:**
- System should provide domain-specific knowledge
- Should reference architectural principles
- Should connect to your community center project
- Should encourage application of knowledge
- Should include sources and references

### **Test 8: Technical Detail Request**
**Input:** "How do I calculate the required square footage?"

**Expected Routing:** `knowledge_with_challenge` → Domain Expert Agent

**Expected Response Type:** `KNOWLEDGE`

**Expected Response Format:**
```json
{
  "response_text": "Let me guide you through the square footage calculation process...",
  "response_type": "KNOWLEDGE",
  "cognitive_flags": ["KNOWLEDGE_PROVIDED", "TECHNICAL_GUIDANCE"],
  "agent_name": "domain_expert",
  "enhancement_metrics": {
    "knowledge_integration_score": 0.85,
    "deep_thinking_engagement_score": 0.8,
    "learning_progression_score": 0.75
  },
  "conversation_progression": {
    "conversation_phase": "application",
    "phase_progress": 0.3
  },
  "metadata": {
    "calculation_method": "step_by_step",
    "formulas": {...},
    "examples": {...}
  }
}
```

**Expected Behavior:**
- System should provide technical guidance
- Should explain the calculation process
- Should encourage you to work through it
- Should not just give the answer
- Should show "⚡ Application" in phase display

### **Test 9: Historical Reference Request**
**Input:** "Can you show me examples of successful community centers?"

**Expected Routing:** `knowledge_only` → Domain Expert Agent

**Expected Response Type:** `KNOWLEDGE`

**Expected Response Format:**
```json
{
  "response_text": "Here are some excellent examples of successful community centers...",
  "response_type": "KNOWLEDGE",
  "cognitive_flags": ["KNOWLEDGE_PROVIDED", "HISTORICAL_REFERENCE"],
  "agent_name": "domain_expert",
  "enhancement_metrics": {
    "knowledge_integration_score": 0.9,
    "deep_thinking_engagement_score": 0.7,
    "learning_progression_score": 0.8
  },
  "conversation_progression": {
    "conversation_phase": "exploration",
    "phase_progress": 0.8
  },
  "metadata": {
    "examples": [
      {"name": "Community Center A", "principles": [...]},
      {"name": "Community Center B", "principles": [...]}
    ],
    "sources": ["Architectural Record", "Design Awards"]
  }
}
```

**Expected Behavior:**
- System should provide relevant examples
- Should explain design principles from examples
- Should encourage analysis of what works
- Should connect to your project
- Should include specific case studies

---

## **Phase 4: Socratic Method Tests**

### **Test 10: Question-Based Learning**
**Input:** "I'm stuck on the circulation flow"
**Expected Behavior:**
- System should ask probing questions
- Should guide you to discover solutions
- Should not provide direct answers
- Should encourage systematic thinking

### **Test 11: Hypothesis Testing**
**Input:** "I think the library should be on the second floor"
**Expected Behavior:**
- System should ask "What's your reasoning?"
- Should encourage you to test your hypothesis
- Should ask about alternatives
- Should guide you to evaluate pros/cons

### **Test 12: Critical Thinking**
**Input:** "Everyone says community centers should have a gym"
**Expected Behavior:**
- System should ask "What evidence supports that?"
- Should encourage critical evaluation
- Should ask about your specific community needs
- Should guide you to question assumptions

---

## **Phase 5: Context Analysis Tests**

### **Test 13: Context Recognition**
**Input:** "Actually, I changed my mind about the location"
**Expected Behavior:**
- System should recognize context change
- Should ask about the new location
- Should adjust guidance accordingly
- Should update project context

### **Test 14: Learning State Detection**
**Input:** "I'm getting confused with all these options"
**Expected Behavior:**
- System should detect confusion state
- Should simplify the approach
- Should provide more structured guidance
- Should check engagement level

### **Test 15: Confidence Assessment**
**Input:** "I'm pretty confident about the exterior design"
**Expected Behavior:**
- System should assess confidence level
- Should ask for justification
- Should check for overconfidence
- Should encourage deeper thinking

---

## **Phase 6: Progress Tracking Tests**

### **Test 16: Phase Progression**
**Input:** "I think I'm ready to move to the next phase"
**Expected Behavior:**
- System should evaluate current progress
- Should check milestone completion
- Should guide phase transition
- Should update progress metrics

### **Test 17: Milestone Achievement**
**Input:** "I've completed the initial concept sketches"
**Expected Behavior:**
- System should acknowledge milestone
- Should assess quality of work
- Should guide next steps
- Should update progress tracking

### **Test 18: Learning Progression**
**Input:** "I feel like I've learned a lot about space planning"
**Expected Behavior:**
- System should acknowledge learning
- Should assess skill development
- Should encourage reflection
- Should update learning metrics

---

## **Phase 7: Advanced Interaction Tests**

### **Test 19: Multi-Aspect Analysis**
**Input:** "I need to consider sustainability, accessibility, and budget"
**Expected Behavior:**
- System should analyze multiple aspects
- Should help prioritize considerations
- Should guide systematic approach
- Should check for comprehensive thinking

### **Test 20: Problem-Solving Process**
**Input:** "I'm having trouble balancing different user needs"
**Expected Behavior:**
- System should guide problem-solving process
- Should encourage systematic analysis
- Should help identify trade-offs
- Should guide decision-making framework

### **Test 21: Creative Thinking**
**Input:** "I want to make this design really innovative"
**Expected Behavior:**
- System should encourage creative thinking
- Should ask about innovation goals
- Should guide creative process
- Should balance innovation with practicality

---

## **Phase 8: Error Handling Tests**

### **Test 22: Vague Input**
**Input:** "I don't know"
**Expected Behavior:**
- System should ask clarifying questions
- Should help you identify what you don't know
- Should provide structure for thinking
- Should not give up or provide answers

### **Test 23: Off-Topic Input**
**Input:** "What's the weather like?"
**Expected Behavior:**
- System should gently redirect to project
- Should maintain focus on architectural design
- Should not engage with off-topic questions
- Should guide back to community center design

### **Test 24: Complex Multi-Part Question**
**Input:** "How do I design the entrance, circulation, and make it sustainable while staying under budget?"
**Expected Behavior:**
- System should break down complex question
- Should address each aspect systematically
- Should guide prioritization
- Should not overwhelm with information

---

## **Phase 9: System Integration Tests**

### **Test 25: Knowledge Integration**
**Input:** "Can you help me apply what we discussed about accessibility to my entrance design?"
**Expected Behavior:**
- System should reference previous discussions
- Should connect knowledge to current task
- Should guide application of concepts
- Should check knowledge integration

### **Test 26: Context Continuity**
**Input:** "Going back to what we said about the elderly users..."
**Expected Behavior:**
- System should maintain context continuity
- Should reference previous discussions
- Should build on established understanding
- Should guide deeper application

### **Test 27: Learning Transfer**
**Input:** "I think the principles we discussed for the library could apply to the meeting rooms"
**Expected Behavior:**
- System should acknowledge learning transfer
- Should encourage application of principles
- Should guide adaptation of concepts
- Should assess understanding depth

---

## **Testing Protocol**

### **Before Each Test:**
1. Clear the chat history (if possible)
2. Start fresh with the initial project setup
3. Follow the conversation flow as specified
4. Monitor sidebar updates after each response
5. Check for any error messages in the terminal

### **During Each Test:**
1. Type the exact input as specified
2. Wait for system response (10-15 seconds)
3. Check sidebar sections for updates:
   - Analysis section
   - Classification section
   - Progress Update section
   - Any error messages
4. Note any unexpected behavior
5. Document response quality and relevance

### **After Each Test:**
1. Evaluate if the response matches expected behavior
2. Check if cognitive enhancement features are working
3. Verify that the system is not providing direct answers when it should guide
4. Note any technical issues or errors
5. Document any improvements needed

---

## **Success Criteria**

### **Cognitive Enhancement Success:**
- System detects and prevents cognitive offloading
- Provides scaffolding instead of direct answers
- Encourages deep thinking and metacognitive awareness
- Maintains appropriate challenge level

### **Domain Knowledge Success:**
- Provides relevant architectural knowledge
- Connects knowledge to the specific project
- Encourages application rather than memorization
- Balances technical detail with accessibility

### **Socratic Method Success:**
- Asks probing questions instead of giving answers
- Guides discovery and learning
- Encourages critical thinking
- Maintains engagement through questioning

### **Progress Tracking Success:**
- Accurately tracks learning progression
- Updates milestones appropriately
- Provides meaningful progress feedback
- Maintains context across interactions

### **System Integration Success:**
- Maintains conversation continuity
- Integrates knowledge across interactions
- Provides coherent guidance
- Handles errors gracefully

---

## **Troubleshooting Guide**

### **If System Doesn't Respond:**
1. Check terminal for error messages
2. Verify OpenAI API key is set
3. Check internet connection
4. Restart the application

### **If Responses Are Inappropriate:**
1. Check if the correct agent is being triggered
2. Verify routing logic is working
3. Check agent response formatting
4. Look for compatibility issues

### **If Sidebar Doesn't Update:**
1. Check data flow from agents to UI
2. Verify AgentResponse conversion
3. Check UI update logic
4. Look for data structure issues

### **If Cognitive Enhancement Isn't Working:**
1. Check cognitive enhancement agent
2. Verify offloading detection logic
3. Check challenge generation
4. Verify response routing

---

## **Expected Timeline**

- **Basic Tests (1-3):** 15-20 minutes
- **Cognitive Tests (4-6):** 20-25 minutes  
- **Domain Tests (7-9):** 25-30 minutes
- **Socratic Tests (10-12):** 20-25 minutes
- **Context Tests (13-15):** 20-25 minutes
- **Progress Tests (16-18):** 15-20 minutes
- **Advanced Tests (19-21):** 25-30 minutes
- **Error Tests (22-24):** 15-20 minutes
- **Integration Tests (25-27):** 20-25 minutes

**Total Estimated Time:** 3-4 hours for comprehensive testing

---

## **Documentation Template**

For each test, document:

```
Test Number: ___
Input: ___
Expected Behavior: ___
Actual Behavior: ___
Sidebar Updates: ___
Errors/Issues: ___
Success Rating (1-5): ___
Notes: ___
```

This will help you track the system's performance and identify areas for improvement.

---

## **Technical Debugging Information**

### **How to Check Routing Decisions**

**In the terminal, look for these log messages:**
```
🎯 Advanced Routing Decision: socratic_exploration
   Reason: User seeking guidance on design process
   Confidence: 0.85
   Rule Applied: Socratic guidance needed for exploration
```

**Expected routing patterns:**
- First message → `progressive_opening`
- Knowledge requests → `knowledge_only` or `knowledge_with_challenge`
- Offloading attempts → `cognitive_intervention`
- Clarification needs → `socratic_clarification`
- Complex analysis → `multi_agent_comprehensive`

### **How to Check Response Types**

**Look for these response types in the UI metadata:**
- `GUIDANCE`: Socratic tutoring responses
- `KNOWLEDGE`: Domain expert responses
- `CHALLENGE`: Cognitive enhancement responses
- `ANALYSIS`: Analysis agent responses
- `SYNTHESIS`: Combined multi-agent responses

### **How to Check Cognitive Flags**

**Expected cognitive flags:**
- `COGNITIVE_OFFLOADING_DETECTED`: When user tries to get direct answers
- `SCAFFOLDING_PROVIDED`: When system provides guidance instead of answers
- `KNOWLEDGE_PROVIDED`: When domain knowledge is shared
- `METACOGNITIVE_AWARENESS_DETECTED`: When user shows self-reflection
- `ANALYSIS_COMPLETED`: When comprehensive analysis is performed

### **How to Check Enhancement Metrics**

**Look for these scores (0-1 scale):**
- `cognitive_offloading_prevention_score`: Should be high (0.8+) for offloading attempts
- `deep_thinking_engagement_score`: Should be high (0.7+) for good responses
- `knowledge_integration_score`: Should be high (0.8+) for knowledge responses
- `scaffolding_effectiveness_score`: Should be high (0.8+) for guidance responses
- `metacognitive_awareness_score`: Should be high (0.8+) for reflection responses

### **How to Check Conversation Progression**

**Expected progression flow:**
1. `discovery` (0-20%): Initial exploration
2. `exploration` (20-60%): Deepening understanding
3. `synthesis` (60-80%): Connecting ideas
4. `application` (80-90%): Applying knowledge
5. `reflection` (90-100%): Evaluating understanding

### **Common Issues and Solutions**

**Issue: "Unknown" phase displayed**
- **Cause**: Conversation progression not integrated
- **Solution**: Check if `conversation_progression` is in the response data

**Issue: No cognitive flags**
- **Cause**: AgentResponse conversion failed
- **Solution**: Check if agents are returning AgentResponse objects

**Issue: Wrong routing**
- **Cause**: AdvancedRoutingDecisionTree not working
- **Solution**: Check terminal logs for routing decisions

**Issue: No enhancement metrics**
- **Cause**: Enhancement metrics calculation failed
- **Solution**: Check if agents are calculating metrics properly

### **Data Flow Verification**

**Expected data flow:**
1. User input → Context Agent
2. Context Agent → Router
3. Router → Appropriate Agent(s)
4. Agent(s) → Synthesizer
5. Synthesizer → UI with conversation progression

**Check each step in the terminal logs:**
```
📝 Processing user input: I want to design a community center...
🎯 Advanced Routing Decision: progressive_opening
🤖 Using Socratic Agent (multi-agent system)...
✅ LangGraph workflow completed!
```

### **Performance Metrics to Monitor**

**Response Time:**
- Should be 10-15 seconds for complex responses
- Should be 5-10 seconds for simple responses

**Agent Usage:**
- Check which agents are being used most
- Verify routing decisions match expected patterns

**Cognitive Enhancement:**
- Monitor offloading prevention success rate
- Track deep thinking engagement scores

**Learning Progression:**
- Verify conversation phases progress correctly
- Check milestone completion rates 