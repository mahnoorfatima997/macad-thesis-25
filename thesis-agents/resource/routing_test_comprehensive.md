# COMPREHENSIVE ROUTING TEST SUITE

## 🎯 EXPECTED ROUTING BEHAVIOR

### **DESIGN GUIDANCE ROUTE** (Should get domain expert knowledge)
```
1. What program elements should I consider for a community center?
   Expected: design_guidance → domain_expert knowledge

2. How should I organize spaces for different age groups?
   Expected: design_guidance → spatial organization guidance

3. What are the key considerations for community center programming?
   Expected: design_guidance → programming knowledge

4. How do I handle circulation patterns in a large community space?
   Expected: design_guidance → circulation design guidance

5. What's the best way to integrate cultural elements into my design?
   Expected: design_guidance → cultural design guidance
```

### **KNOWLEDGE REQUEST ROUTE** (Should get domain expert knowledge)
```
6. What are passive cooling strategies for large buildings?
   Expected: knowledge_only → technical knowledge

7. What materials work best in Mediterranean climates?
   Expected: knowledge_only → material knowledge

8. How do other architects handle warehouse conversions?
   Expected: knowledge_only → precedent knowledge

9. What building codes apply to community centers?
   Expected: knowledge_only → regulatory knowledge

10. What HVAC systems work for large community spaces?
    Expected: knowledge_only → technical systems knowledge
```

### **EXAMPLE REQUEST ROUTE** (Should get specific project examples)
```
11. Can you give example projects for community centers in hot climates?
    Expected: example_request → specific project examples

12. Show me examples of warehouse-to-community center conversions?
    Expected: example_request → adaptive reuse examples

13. What are some successful intergenerational community spaces?
    Expected: example_request → typological examples

14. Give me precedents for adaptive reuse projects in Spain?
    Expected: example_request → regional examples

15. Can you show me community centers that work well for all ages?
    Expected: example_request → age-inclusive examples
```

### **FEEDBACK REQUEST ROUTE** (Should get constructive analysis)
```
16. Can you give me feedback on my zoning concept?
    Expected: feedback_request → design analysis

17. What do you think about using existing trusses as features?
    Expected: feedback_request → structural feedback

18. Is my approach to climate control appropriate?
    Expected: feedback_request → technical feedback

19. How can I improve my spatial organization?
    Expected: feedback_request → design improvement

20. Does my programming make sense for this building type?
    Expected: feedback_request → programming analysis
```

### **CONFUSION EXPRESSION ROUTE** (Should get supportive scaffolding)
```
21. I'm confused about balancing preservation with modern needs
    Expected: confusion_expression → supportive guidance

22. I don't understand how to make this work for all ages
    Expected: confusion_expression → clarification support

23. This is overwhelming - there are so many requirements
    Expected: confusion_expression → emotional support

24. I'm lost on where to start with climate response
    Expected: confusion_expression → directional guidance

25. I can't figure out how to organize all these programs
    Expected: confusion_expression → organizational support
```

### **SOCRATIC EXPLORATION ROUTE** (Should get guided questioning)
```
26. I'm exploring different approaches to the entrance design
    Expected: socratic_exploration → guided questions

27. I'm thinking about how to connect indoor and outdoor spaces
    Expected: socratic_exploration → relationship questions

28. I'm considering various ways to organize program spaces
    Expected: socratic_exploration → organizational questions

29. I'm analyzing how different user groups might interact
    Expected: socratic_exploration → interaction analysis

30. I'm investigating flexible space solutions
    Expected: socratic_exploration → flexibility exploration
```

### **GAMIFICATION TRIGGERS** (Should show enhanced visuals)
```
31. How would a visitor feel entering my community center?
    Expected: cognitive_challenge → role-play gamification

32. What would an elderly person think about my design?
    Expected: cognitive_challenge → perspective shift

33. I wonder what would happen if I made the entrance dramatic?
    Expected: cognitive_challenge → curiosity amplification

34. I'm stuck on handling the hot climate
    Expected: cognitive_challenge → creative constraint

35. This seems pretty easy to solve
    Expected: cognitive_challenge → reality check

36. Ok
    Expected: cognitive_challenge → low engagement
```

### **PHASE PROGRESSION** (Should advance through phases)
```
37. The primary purpose is creating multifunctional space for all ages
    Expected: ideation phase scoring

38. I envision the main hall with preserved high ceilings
    Expected: visualization phase transition

39. For hot climate, I'm considering thick walls with thermal mass
    Expected: materialization phase transition
```

## 🚨 CURRENT ISSUES IDENTIFIED

### **BROKEN ROUTING EXAMPLES:**
```
❌ "What program elements should I consider?" 
   Current: general_statement → socratic_exploration
   Should be: design_guidance → domain_expert knowledge

❌ "How should I organize spaces?"
   Current: general_statement → socratic_exploration  
   Should be: design_guidance → spatial guidance

❌ "What are passive cooling strategies?"
   Current: general_statement → socratic_exploration
   Should be: knowledge_only → technical knowledge
```

## 🔧 TESTING PROTOCOL

### **Step 1: Test Each Input**
1. Copy each test input above
2. Paste into chat interface
3. Record actual routing result from metadata
4. Compare with expected result

### **Step 2: Document Failures**
For each failed test, record:
- Input text
- Expected route
- Actual route  
- Agents activated
- Response type

### **Step 3: Pattern Analysis**
Look for patterns in failures:
- Are all knowledge requests being misclassified?
- Is intent extraction working?
- Are routing patterns too broad/narrow?

## 📊 RESULTS TRACKING

### **SUCCESS RATE BY CATEGORY:**
- Design Guidance: ___/5 correct
- Knowledge Request: ___/5 correct  
- Example Request: ___/5 correct
- Feedback Request: ___/5 correct
- Confusion Expression: ___/5 correct
- Socratic Exploration: ___/5 correct
- Gamification: ___/6 correct
- Phase Progression: ___/3 correct

### **OVERALL SUCCESS RATE:** ___/39 total

## 🎯 SUCCESS CRITERIA

**PASSING GRADE:** 80% success rate (31/39 correct)
**CURRENT ESTIMATE:** <50% (based on observed issues)

**CRITICAL FIXES NEEDED:**
1. Intent extraction improvements
2. Routing pattern refinements  
3. Agent selection logic
4. Response type classification
