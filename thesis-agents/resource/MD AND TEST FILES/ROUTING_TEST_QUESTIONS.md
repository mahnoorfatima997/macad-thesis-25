# Routing Test Questions

## **Test Questions to Verify All Routing Logic**

### **1. First Message Tests (Should route to `progressive_opening`)**
- "I'm starting a new architectural project"
- "Hello, I need help with my design"
- "I want to learn about sustainable architecture"

### **2. Technical Questions (Should route to `socratic_clarification` or `knowledge_with_challenge`)**
- "What are the best materials for a community center?"
- "How do I calculate the structural load for a cantilever?"
- "What's the optimal window-to-wall ratio for energy efficiency?"
- "How should I approach acoustic design in an open-plan office?"

### **3. General Questions (Should route to `socratic_exploration` or `knowledge_with_challenge`)**
- "What makes a good public space?"
- "How do I create a welcoming entrance?"
- "What should I consider when designing for accessibility?"
- "How can I make my design more sustainable?"

### **4. Confusion/Struggle (Should route to `supportive_scaffolding`)**
- "I'm confused about how to start this project"
- "I don't know what to do next"
- "I'm stuck on this design problem"
- "I'm not sure if this approach is right"

### **5. Knowledge Requests (Should route to `knowledge_only`)**
- "What are some examples of adaptive reuse projects?"
- "Can you show me some community center precedents?"
- "What are the principles of biophilic design?"
- "Give me some examples of sustainable building materials"

### **6. Direct Answer Requests (Should route to `cognitive_intervention`)**
- "Just tell me what to do"
- "Give me the answer"
- "What should I design?"
- "Do it for me"

### **7. Implementation Requests (Should route to `knowledge_with_challenge` or `foundational_building`)**
- "How do I implement passive solar design?"
- "What are the steps to create a site analysis?"
- "How do I start the schematic design phase?"
- "What's the process for selecting materials?"

### **8. Evaluation Requests (Should route to `multi_agent_comprehensive`)**
- "Is this a good design approach?"
- "Should I use this material?"
- "Will this layout work?"
- "Is this the right solution?"

### **9. Creative Exploration (Should route to `socratic_exploration`)**
- "What if I tried a different approach?"
- "How could I make this more innovative?"
- "What are some alternative solutions?"
- "How can I think outside the box?"

### **10. Design Problems (Should route to `socratic_exploration` or `supportive_scaffolding`)**
- "I'm having trouble with the circulation"
- "The budget is too tight for my design"
- "The site constraints are challenging"
- "I can't figure out how to make it accessible"

### **11. Example Requests (Should route to `knowledge_only`)**
- "Show me some examples"
- "Can you give me some precedents?"
- "I need some inspiration"
- "What are some similar projects?"

### **12. Clarification Requests (Should route to `socratic_clarification`)**
- "Can you explain that further?"
- "I don't understand what you mean"
- "Could you clarify that point?"
- "What do you mean by that?"

## **Expected Routing Patterns**

### **High Understanding + Technical Question** → `knowledge_with_challenge`
### **Medium Understanding + Technical Question** → `socratic_clarification`
### **Low Understanding + Technical Question** → `socratic_clarification`
### **High Engagement + General Question** → `socratic_exploration`
### **Medium Engagement + General Question** → `knowledge_with_challenge`
### **Low Engagement + General Question** → `supportive_scaffolding`
### **Confusion Expression** → `supportive_scaffolding`
### **Cognitive Offloading** → `cognitive_intervention`
### **Pure Knowledge Request** → `knowledge_only`
### **Knowledge + Guidance Request** → `socratic_exploration`

## **Testing Instructions**

1. **Start with first message** - Should always route to `progressive_opening`
2. **Test each interaction type** - Use the questions above to test different routing paths
3. **Check response quality** - Ensure responses are contextual and reference user details
4. **Verify web links** - For knowledge requests, ensure web links are included
5. **Test conversation flow** - Ensure routing changes appropriately as conversation progresses

## **Success Criteria**

- ✅ Different interaction types route to different paths
- ✅ Responses are contextual and reference user details
- ✅ Web links are included for knowledge requests
- ✅ No repetitive examples
- ✅ Progress tracking works correctly
- ✅ Response quality is high and specific
